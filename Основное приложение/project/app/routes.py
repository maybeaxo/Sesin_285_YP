from __future__ import annotations

from datetime import date
from urllib.parse import urlencode

from flask import (
    abort,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import String, and_, cast, or_
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from .decorators import role_required
from .extensions import db
from .models import (
    REQUEST_STATUSES,
    Client,
    Equipment,
    FaultType,
    FeedbackReview,
    Master,
    OrderedPart,
    Request,
    RequestCollaborator,
    RequestComment,
    RequestDetail,
    Role,
    StatusNotification,
    User,
)
from .services import calculate_statistics, generate_qr_code, parse_date, status_label


QUALITY_FORM_URL = (
    "https://docs.google.com/forms/d/e/1FAIpQLSdhZcExx6LSIXxk0ub55mSu-WIh23WYdGG9HY5EZhLDo7P8eA/"
    "viewform?usp=sf_link"
)


def _safe_commit(success_message: str, error_message: str) -> bool:
    try:
        db.session.commit()
        flash(success_message, "success")
        return True
    except IntegrityError:
        db.session.rollback()
        flash(error_message, "danger")
        return False
    except Exception:
        db.session.rollback()
        flash("Произошла ошибка при сохранении данных.", "danger")
        return False


def _parse_fault_type_ids(values: list[str]) -> list[int]:
    fault_ids = []
    for value in values:
        if value.isdigit():
            fault_ids.append(int(value))
    return fault_ids


def _create_notification(request_obj: Request, old_status: str, new_status: str, user: User) -> None:
    message = (
        f"Заявка №{request_obj.request_id}: статус изменен с "
        f"'{status_label(old_status)}' на '{status_label(new_status)}'."
    )
    db.session.add(
        StatusNotification(
            request_id=request_obj.request_id,
            user_id=user.user_id,
            old_status=old_status,
            new_status=new_status,
            message=message,
        )
    )


def _has_master_access_to_request(user: User, request_obj: Request) -> bool:
    if user.role_name != "master":
        return True
    if user.master_id is None:
        return False
    if request_obj.master_id == user.master_id:
        return True
    collaborator_exists = RequestCollaborator.query.filter_by(
        request_id=request_obj.request_id,
        master_id=user.master_id,
    ).first()
    return collaborator_exists is not None


def _visible_notifications_query(user: User):
    notifications_query = StatusNotification.query.order_by(StatusNotification.created_at.desc())
    if user.role_name != "master":
        return notifications_query
    if user.master_id is None:
        return notifications_query.filter(False)

    assigned_ids = (
        Request.query.with_entities(Request.request_id)
        .filter(Request.master_id == user.master_id)
        .all()
    )
    collab_ids = (
        RequestCollaborator.query.with_entities(RequestCollaborator.request_id)
        .filter(RequestCollaborator.master_id == user.master_id)
        .all()
    )
    allowed_request_ids = {row[0] for row in assigned_ids}
    allowed_request_ids.update(row[0] for row in collab_ids)
    if not allowed_request_ids:
        return notifications_query.filter(False)
    return notifications_query.filter(StatusNotification.request_id.in_(allowed_request_ids))


def register_routes(app):
    @app.context_processor
    def inject_common_context():
        if not current_user.is_authenticated:
            return {
                "status_label": status_label,
                "request_statuses": REQUEST_STATUSES,
                "navbar_notifications": [],
                "navbar_notification_count": 0,
            }

        notifications_query = _visible_notifications_query(current_user)
        navbar_notifications = notifications_query.limit(7).all()
        navbar_notification_count = notifications_query.count()
        return {
            "status_label": status_label,
            "request_statuses": REQUEST_STATUSES,
            "navbar_notifications": navbar_notifications,
            "navbar_notification_count": navbar_notification_count,
        }

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        return redirect(url_for("login"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            login_value = request.form.get("login", "").strip()
            password_value = request.form.get("password", "")

            user = User.query.filter_by(login=login_value).first()
            if user is None or not check_password_hash(user.password_hash, password_value):
                flash("Неверный логин или пароль.", "danger")
                return render_template("auth_login.html")

            login_user(user)
            flash("Вы успешно вошли в систему.", "success")
            return redirect(url_for("dashboard"))

        return render_template("auth_login.html")

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("Сеанс завершен.", "info")
        return redirect(url_for("login"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        base_query = Request.query
        if current_user.role_name == "master":
            if current_user.master_id is None:
                base_query = base_query.filter(False)
            else:
                base_query = base_query.outerjoin(
                    RequestCollaborator,
                    and_(
                        RequestCollaborator.request_id == Request.request_id,
                        RequestCollaborator.master_id == current_user.master_id,
                    ),
                ).filter(
                    or_(
                        Request.master_id == current_user.master_id,
                        RequestCollaborator.master_id == current_user.master_id,
                    )
                )

        requests_data = base_query.all()
        stats = {
            "open": sum(1 for r in requests_data if r.status == "open"),
            "in_progress": sum(1 for r in requests_data if r.status == "in_progress"),
            "waiting_parts": sum(1 for r in requests_data if r.status == "waiting_parts"),
            "completed": sum(1 for r in requests_data if r.status == "completed"),
            "total": len(requests_data),
        }

        notifications = _visible_notifications_query(current_user).limit(10).all()
        return render_template("dashboard.html", stats=stats, notifications=notifications)

    @app.route("/clients")
    @login_required
    @role_required("admin", "operator", "manager")
    def clients_list():
        search = request.args.get("search", "").strip()
        query = Client.query
        if search:
            like = f"%{search}%"
            query = query.filter(
                or_(
                    Client.full_name.ilike(like),
                    Client.phone.ilike(like),
                    Client.email.ilike(like),
                    Client.address.ilike(like),
                )
            )

        clients = query.order_by(Client.full_name).all()
        return render_template("clients_list.html", clients=clients, search=search)

    @app.route("/clients/new", methods=["GET", "POST"])
    @login_required
    @role_required("admin", "operator", "manager")
    def clients_new():
        if request.method == "POST":
            full_name = request.form.get("full_name", "").strip()
            phone = request.form.get("phone", "").strip()
            email = request.form.get("email", "").strip()
            address = request.form.get("address", "").strip()

            if not full_name or not phone:
                flash("ФИО и телефон клиента обязательны.", "warning")
                return render_template("clients_form.html", client=None)

            db.session.add(
                Client(
                    full_name=full_name,
                    phone=phone,
                    email=email or None,
                    address=address or None,
                )
            )
            if _safe_commit("Клиент добавлен.", "Не удалось добавить клиента."):
                return redirect(url_for("clients_list"))

        return render_template("clients_form.html", client=None)

    @app.route("/clients/<int:client_id>/edit", methods=["GET", "POST"])
    @login_required
    @role_required("admin", "operator", "manager")
    def clients_edit(client_id: int):
        client = Client.query.get_or_404(client_id)

        if request.method == "POST":
            full_name = request.form.get("full_name", "").strip()
            phone = request.form.get("phone", "").strip()
            email = request.form.get("email", "").strip()
            address = request.form.get("address", "").strip()

            if not full_name or not phone:
                flash("ФИО и телефон клиента обязательны.", "warning")
                return render_template("clients_form.html", client=client)

            client.full_name = full_name
            client.phone = phone
            client.email = email or None
            client.address = address or None

            if _safe_commit("Данные клиента обновлены.", "Не удалось обновить данные клиента."):
                return redirect(url_for("clients_list"))

        return render_template("clients_form.html", client=client)

    @app.route("/equipment")
    @login_required
    @role_required("admin", "operator", "manager")
    def equipment_list():
        search = request.args.get("search", "").strip()
        query = Equipment.query.join(Client)

        if search:
            like = f"%{search}%"
            query = query.filter(
                or_(
                    Equipment.model.ilike(like),
                    Equipment.serial_number.ilike(like),
                    Equipment.equipment_type.ilike(like),
                    Client.full_name.ilike(like),
                )
            )

        equipment_items = query.order_by(Equipment.equipment_id.desc()).all()
        return render_template(
            "equipment_list.html",
            equipment_items=equipment_items,
            search=search,
        )

    @app.route("/equipment/new", methods=["GET", "POST"])
    @login_required
    @role_required("admin", "operator", "manager")
    def equipment_new():
        clients = Client.query.order_by(Client.full_name).all()

        if request.method == "POST":
            model = request.form.get("model", "").strip()
            serial_number = request.form.get("serial_number", "").strip()
            equipment_type = request.form.get("equipment_type", "").strip()
            client_id = request.form.get("client_id", "").strip()

            if not model or not serial_number or not equipment_type or not client_id.isdigit():
                flash("Заполните все обязательные поля оборудования.", "warning")
                return render_template("equipment_form.html", equipment=None, clients=clients)

            db.session.add(
                Equipment(
                    model=model,
                    serial_number=serial_number,
                    equipment_type=equipment_type,
                    client_id=int(client_id),
                )
            )
            if _safe_commit(
                "Оборудование добавлено.",
                "Не удалось добавить оборудование. Проверьте уникальность серийного номера.",
            ):
                return redirect(url_for("equipment_list"))

        return render_template("equipment_form.html", equipment=None, clients=clients)

    @app.route("/equipment/<int:equipment_id>/edit", methods=["GET", "POST"])
    @login_required
    @role_required("admin", "operator", "manager")
    def equipment_edit(equipment_id: int):
        equipment_obj = Equipment.query.get_or_404(equipment_id)
        clients = Client.query.order_by(Client.full_name).all()

        if request.method == "POST":
            model = request.form.get("model", "").strip()
            serial_number = request.form.get("serial_number", "").strip()
            equipment_type = request.form.get("equipment_type", "").strip()
            client_id = request.form.get("client_id", "").strip()

            if not model or not serial_number or not equipment_type or not client_id.isdigit():
                flash("Заполните все обязательные поля оборудования.", "warning")
                return render_template(
                    "equipment_form.html",
                    equipment=equipment_obj,
                    clients=clients,
                )

            equipment_obj.model = model
            equipment_obj.serial_number = serial_number
            equipment_obj.equipment_type = equipment_type
            equipment_obj.client_id = int(client_id)

            if _safe_commit(
                "Оборудование обновлено.",
                "Не удалось обновить оборудование. Проверьте уникальность серийного номера.",
            ):
                return redirect(url_for("equipment_list"))

        return render_template("equipment_form.html", equipment=equipment_obj, clients=clients)

    @app.route("/masters")
    @login_required
    @role_required("admin", "operator", "manager")
    def masters_list():
        search = request.args.get("search", "").strip()
        query = Master.query
        if search:
            like = f"%{search}%"
            query = query.filter(
                or_(
                    Master.full_name.ilike(like),
                    Master.specialization.ilike(like),
                    Master.phone.ilike(like),
                )
            )

        masters = query.order_by(Master.full_name).all()
        return render_template("masters_list.html", masters=masters, search=search)

    @app.route("/masters/new", methods=["GET", "POST"])
    @login_required
    @role_required("admin", "manager")
    def masters_new():
        if request.method == "POST":
            full_name = request.form.get("full_name", "").strip()
            specialization = request.form.get("specialization", "").strip()
            phone = request.form.get("phone", "").strip()

            if not full_name or not specialization or not phone:
                flash("Все поля мастера обязательны.", "warning")
                return render_template("masters_form.html", master=None)

            db.session.add(
                Master(
                    full_name=full_name,
                    specialization=specialization,
                    phone=phone,
                )
            )
            if _safe_commit("Мастер добавлен.", "Не удалось добавить мастера."):
                return redirect(url_for("masters_list"))

        return render_template("masters_form.html", master=None)

    @app.route("/masters/<int:master_id>/edit", methods=["GET", "POST"])
    @login_required
    @role_required("admin", "manager")
    def masters_edit(master_id: int):
        master = Master.query.get_or_404(master_id)

        if request.method == "POST":
            full_name = request.form.get("full_name", "").strip()
            specialization = request.form.get("specialization", "").strip()
            phone = request.form.get("phone", "").strip()

            if not full_name or not specialization or not phone:
                flash("Все поля мастера обязательны.", "warning")
                return render_template("masters_form.html", master=master)

            master.full_name = full_name
            master.specialization = specialization
            master.phone = phone

            if _safe_commit("Данные мастера обновлены.", "Не удалось обновить данные мастера."):
                return redirect(url_for("masters_list"))

        return render_template("masters_form.html", master=master)

    @app.route("/users")
    @login_required
    @role_required("admin")
    def users_list():
        users = User.query.join(Role).outerjoin(Master).order_by(User.login).all()
        return render_template("users_list.html", users=users)

    @app.route("/users/new", methods=["GET", "POST"])
    @login_required
    @role_required("admin")
    def users_new():
        roles = Role.query.order_by(Role.role_name).all()
        masters = Master.query.order_by(Master.full_name).all()

        if request.method == "POST":
            login_value = request.form.get("login", "").strip()
            password_value = request.form.get("password", "")
            role_id = request.form.get("role_id", "").strip()
            master_id = request.form.get("master_id", "").strip()

            if not login_value or not password_value or not role_id.isdigit():
                flash("Логин, пароль и роль обязательны.", "warning")
                return render_template("users_form.html", user=None, roles=roles, masters=masters)

            assigned_master_id = int(master_id) if master_id.isdigit() else None
            user = User(
                login=login_value,
                password_hash=generate_password_hash(password_value),
                role_id=int(role_id),
                master_id=assigned_master_id,
            )
            db.session.add(user)
            if _safe_commit(
                "Пользователь добавлен.",
                "Не удалось добавить пользователя. Проверьте уникальность логина.",
            ):
                return redirect(url_for("users_list"))

        return render_template("users_form.html", user=None, roles=roles, masters=masters)

    @app.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
    @login_required
    @role_required("admin")
    def users_edit(user_id: int):
        user_obj = User.query.get_or_404(user_id)
        roles = Role.query.order_by(Role.role_name).all()
        masters = Master.query.order_by(Master.full_name).all()

        if request.method == "POST":
            login_value = request.form.get("login", "").strip()
            password_value = request.form.get("password", "")
            role_id = request.form.get("role_id", "").strip()
            master_id = request.form.get("master_id", "").strip()

            if not login_value or not role_id.isdigit():
                flash("Логин и роль обязательны.", "warning")
                return render_template(
                    "users_form.html",
                    user=user_obj,
                    roles=roles,
                    masters=masters,
                )

            user_obj.login = login_value
            user_obj.role_id = int(role_id)
            user_obj.master_id = int(master_id) if master_id.isdigit() else None
            if password_value:
                user_obj.password_hash = generate_password_hash(password_value)

            if _safe_commit(
                "Пользователь обновлен.",
                "Не удалось обновить пользователя. Проверьте уникальность логина.",
            ):
                return redirect(url_for("users_list"))

        return render_template("users_form.html", user=user_obj, roles=roles, masters=masters)

    @app.route("/requests")
    @login_required
    def requests_list():
        query_text = request.args.get("q", "").strip()
        status_filter = request.args.get("status", "").strip()
        master_filter = request.args.get("master_id", "").strip()

        query = Request.query.join(Equipment).join(Client).outerjoin(Master)

        if current_user.role_name == "master":
            if current_user.master_id is None:
                query = query.filter(False)
            else:
                query = query.outerjoin(
                    RequestCollaborator,
                    and_(
                        RequestCollaborator.request_id == Request.request_id,
                        RequestCollaborator.master_id == current_user.master_id,
                    ),
                ).filter(
                    or_(
                        Request.master_id == current_user.master_id,
                        RequestCollaborator.master_id == current_user.master_id,
                    )
                )

        if query_text:
            like = f"%{query_text}%"
            query = query.filter(
                or_(
                    cast(Request.request_id, String).ilike(like),
                    Request.description.ilike(like),
                    Equipment.model.ilike(like),
                    Equipment.serial_number.ilike(like),
                    Equipment.equipment_type.ilike(like),
                    Client.full_name.ilike(like),
                    Client.phone.ilike(like),
                )
            )

        if status_filter in REQUEST_STATUSES:
            query = query.filter(Request.status == status_filter)

        if master_filter.isdigit() and current_user.role_name != "master":
            query = query.filter(Request.master_id == int(master_filter))

        requests_items = query.order_by(Request.request_id.desc()).all()
        masters = Master.query.order_by(Master.full_name).all()

        return render_template(
            "requests_list.html",
            requests_items=requests_items,
            query_text=query_text,
            status_filter=status_filter,
            master_filter=master_filter,
            masters=masters,
        )

    @app.route("/requests/new", methods=["GET", "POST"])
    @login_required
    @role_required("admin", "operator", "manager")
    def requests_new():
        masters = Master.query.order_by(Master.full_name).all()
        fault_types = FaultType.query.order_by(FaultType.fault_name).all()

        if request.method == "POST":
            create_date_value = parse_date(request.form.get("create_date", "").strip()) or date.today()
            description = request.form.get("description", "").strip()
            status_value = request.form.get("status", "open").strip()
            deadline_date_value = parse_date(request.form.get("deadline_date", "").strip())

            client_full_name = request.form.get("client_full_name", "").strip()
            client_phone = request.form.get("client_phone", "").strip()
            client_email = request.form.get("client_email", "").strip()
            client_address = request.form.get("client_address", "").strip()

            equipment_type = request.form.get("equipment_type", "").strip()
            equipment_model = request.form.get("equipment_model", "").strip()
            serial_number = request.form.get("serial_number", "").strip()

            master_id_value = request.form.get("master_id", "").strip()
            fault_ids = _parse_fault_type_ids(request.form.getlist("fault_type_ids"))

            if (
                not description
                or not client_full_name
                or not client_phone
                or not equipment_type
                or not equipment_model
                or not serial_number
            ):
                flash("Заполните обязательные поля заявки, клиента и оборудования.", "warning")
                return render_template(
                    "requests_form.html",
                    request_item=None,
                    masters=masters,
                    fault_types=fault_types,
                    selected_faults=fault_ids,
                )

            if status_value not in REQUEST_STATUSES:
                status_value = "open"

            client = Client.query.filter_by(full_name=client_full_name, phone=client_phone).first()
            if client is None:
                client = Client(
                    full_name=client_full_name,
                    phone=client_phone,
                    email=client_email or None,
                    address=client_address or None,
                )
                db.session.add(client)
                db.session.flush()
            else:
                client.email = client_email or client.email
                client.address = client_address or client.address

            equipment = Equipment.query.filter_by(serial_number=serial_number).first()
            if equipment is None:
                equipment = Equipment(
                    model=equipment_model,
                    serial_number=serial_number,
                    client_id=client.client_id,
                    equipment_type=equipment_type,
                )
                db.session.add(equipment)
                db.session.flush()
            else:
                equipment.model = equipment_model
                equipment.equipment_type = equipment_type
                equipment.client_id = client.client_id

            assigned_master_id = int(master_id_value) if master_id_value.isdigit() else None
            request_item = Request(
                create_date=create_date_value,
                description=description,
                equipment_id=equipment.equipment_id,
                master_id=assigned_master_id,
                status=status_value,
                deadline_date=deadline_date_value,
            )
            db.session.add(request_item)
            db.session.flush()

            for fault_id in fault_ids:
                if db.session.get(FaultType, fault_id):
                    db.session.add(
                        RequestDetail(
                            request_id=request_item.request_id,
                            fault_type_id=fault_id,
                        )
                    )

            if status_value == "completed":
                request_item.completion_date = date.today()

            if _safe_commit("Заявка добавлена.", "Не удалось добавить заявку."):
                return redirect(url_for("requests_detail", request_id=request_item.request_id))

        return render_template(
            "requests_form.html",
            request_item=None,
            masters=masters,
            fault_types=fault_types,
            selected_faults=[],
        )

    @app.route("/requests/<int:request_id>")
    @login_required
    def requests_detail(request_id: int):
        request_item = Request.query.get_or_404(request_id)
        if not _has_master_access_to_request(current_user, request_item):
            abort(403)

        collaborators = (
            RequestCollaborator.query.filter_by(request_id=request_id)
            .join(Master)
            .order_by(Master.full_name)
            .all()
        )
        details = (
            RequestDetail.query.filter_by(request_id=request_id)
            .join(FaultType)
            .order_by(FaultType.fault_name)
            .all()
        )
        comments = (
            RequestComment.query.filter_by(request_id=request_id)
            .order_by(RequestComment.created_at.desc())
            .all()
        )
        parts = (
            OrderedPart.query.filter_by(request_id=request_id)
            .order_by(OrderedPart.ordered_at.desc())
            .all()
        )
        notifications = (
            StatusNotification.query.filter_by(request_id=request_id)
            .order_by(StatusNotification.created_at.desc())
            .all()
        )
        all_masters = Master.query.order_by(Master.full_name).all()

        return render_template(
            "requests_detail.html",
            request_item=request_item,
            collaborators=collaborators,
            details=details,
            comments=comments,
            parts=parts,
            notifications=notifications,
            all_masters=all_masters,
        )

    @app.route("/requests/<int:request_id>/edit", methods=["GET", "POST"])
    @login_required
    @role_required("admin", "operator", "manager")
    def requests_edit(request_id: int):
        request_item = Request.query.get_or_404(request_id)
        masters = Master.query.order_by(Master.full_name).all()
        fault_types = FaultType.query.order_by(FaultType.fault_name).all()

        if request.method == "POST":
            description = request.form.get("description", "").strip()
            status_value = request.form.get("status", "").strip()
            master_id_value = request.form.get("master_id", "").strip()
            deadline_date_value = parse_date(request.form.get("deadline_date", "").strip())
            customer_approved_extension = request.form.get("customer_approved_extension") == "on"
            fault_ids = _parse_fault_type_ids(request.form.getlist("fault_type_ids"))

            if not description:
                flash("Описание проблемы обязательно.", "warning")
                selected_faults = [d.fault_type_id for d in request_item.details]
                return render_template(
                    "requests_form.html",
                    request_item=request_item,
                    masters=masters,
                    fault_types=fault_types,
                    selected_faults=selected_faults,
                )

            old_status = request_item.status
            request_item.description = description
            request_item.deadline_date = deadline_date_value
            request_item.customer_approved_extension = customer_approved_extension
            request_item.master_id = int(master_id_value) if master_id_value.isdigit() else None

            if status_value not in REQUEST_STATUSES:
                status_value = old_status
            request_item.status = status_value

            if status_value == "completed":
                request_item.completion_date = request_item.completion_date or date.today()
            else:
                request_item.completion_date = None

            RequestDetail.query.filter_by(request_id=request_item.request_id).delete()
            for fault_id in fault_ids:
                if db.session.get(FaultType, fault_id):
                    db.session.add(
                        RequestDetail(
                            request_id=request_item.request_id,
                            fault_type_id=fault_id,
                        )
                    )

            if old_status != status_value:
                _create_notification(request_item, old_status, status_value, current_user)

            if _safe_commit("Заявка обновлена.", "Не удалось обновить заявку."):
                return redirect(url_for("requests_detail", request_id=request_item.request_id))

        selected_faults = [d.fault_type_id for d in request_item.details]
        return render_template(
            "requests_form.html",
            request_item=request_item,
            masters=masters,
            fault_types=fault_types,
            selected_faults=selected_faults,
        )

    @app.route("/requests/<int:request_id>/comment", methods=["POST"])
    @login_required
    @role_required("admin", "manager", "master")
    def requests_add_comment(request_id: int):
        request_item = Request.query.get_or_404(request_id)
        if not _has_master_access_to_request(current_user, request_item):
            abort(403)

        comment_text = request.form.get("comment_text", "").strip()
        if not comment_text:
            flash("Комментарий не может быть пустым.", "warning")
            return redirect(url_for("requests_detail", request_id=request_id))

        db.session.add(
            RequestComment(
                request_id=request_item.request_id,
                user_id=current_user.user_id,
                comment_text=comment_text,
            )
        )

        _safe_commit("Комментарий добавлен.", "Не удалось добавить комментарий.")
        return redirect(url_for("requests_detail", request_id=request_id))

    @app.route("/requests/<int:request_id>/parts", methods=["POST"])
    @login_required
    @role_required("admin", "manager", "master")
    def requests_add_part(request_id: int):
        request_item = Request.query.get_or_404(request_id)
        if not _has_master_access_to_request(current_user, request_item):
            abort(403)

        part_name = request.form.get("part_name", "").strip()
        quantity_value = request.form.get("quantity", "").strip()
        notes = request.form.get("notes", "").strip()

        if not part_name or not quantity_value.isdigit() or int(quantity_value) <= 0:
            flash("Укажите корректное название и количество комплектующих.", "warning")
            return redirect(url_for("requests_detail", request_id=request_id))

        db.session.add(
            OrderedPart(
                request_id=request_item.request_id,
                part_name=part_name,
                quantity=int(quantity_value),
                notes=notes or None,
            )
        )

        _safe_commit("Информация о комплектующих сохранена.", "Не удалось сохранить комплектующие.")
        return redirect(url_for("requests_detail", request_id=request_id))

    @app.route("/requests/<int:request_id>/collaborators", methods=["POST"])
    @login_required
    @role_required("admin", "manager")
    def requests_add_collaborator(request_id: int):
        request_item = Request.query.get_or_404(request_id)
        master_id_value = request.form.get("master_id", "").strip()

        if not master_id_value.isdigit():
            flash("Выберите специалиста для привлечения.", "warning")
            return redirect(url_for("requests_detail", request_id=request_id))

        master_id = int(master_id_value)
        if db.session.get(Master, master_id) is None:
            flash("Выбранный специалист не найден.", "warning")
            return redirect(url_for("requests_detail", request_id=request_id))

        if RequestCollaborator.query.filter_by(request_id=request_id, master_id=master_id).first():
            flash("Специалист уже привлечен к заявке.", "info")
            return redirect(url_for("requests_detail", request_id=request_id))

        db.session.add(RequestCollaborator(request_id=request_id, master_id=master_id))
        _safe_commit("Специалист привлечен к ремонту.", "Не удалось привлечь специалиста.")
        return redirect(url_for("requests_detail", request_id=request_id))

    @app.route("/requests/<int:request_id>/extend", methods=["POST"])
    @login_required
    @role_required("admin", "manager")
    def requests_extend_deadline(request_id: int):
        request_item = Request.query.get_or_404(request_id)
        deadline_date_value = parse_date(request.form.get("deadline_date", "").strip())
        customer_approved = request.form.get("customer_approved_extension") == "on"

        if deadline_date_value is None:
            flash("Укажите корректную новую дату срока.", "warning")
            return redirect(url_for("requests_detail", request_id=request_id))

        request_item.deadline_date = deadline_date_value
        request_item.customer_approved_extension = customer_approved

        if request_item.status == "completed":
            flash("Для завершенной заявки продление срока не требуется.", "info")
            return redirect(url_for("requests_detail", request_id=request_id))

        if request_item.status != "waiting_parts":
            old_status = request_item.status
            request_item.status = "waiting_parts"
            _create_notification(request_item, old_status, "waiting_parts", current_user)

        if _safe_commit("Срок выполнения заявки обновлен.", "Не удалось продлить срок заявки."):
            return redirect(url_for("requests_detail", request_id=request_id))

        return redirect(url_for("requests_detail", request_id=request_id))

    @app.route("/notifications")
    @login_required
    def notifications_list():
        notifications = _visible_notifications_query(current_user).limit(100).all()
        return render_template("notifications_list.html", notifications=notifications)

    @app.route("/stats")
    @login_required
    @role_required("admin", "operator", "manager")
    def stats_page():
        stats = calculate_statistics()
        return render_template("stats.html", stats=stats)

    @app.route("/quality")
    @login_required
    def quality_page():
        request_id_value = request.args.get("request_id", "").strip()
        query_params = {}
        if request_id_value.isdigit():
            query_params["entry.123456789"] = request_id_value

        if query_params:
            quality_url = f"{QUALITY_FORM_URL}&{urlencode(query_params)}"
        else:
            quality_url = QUALITY_FORM_URL

        return render_template("quality.html", quality_url=quality_url)

    @app.route("/quality/qr.svg")
    @login_required
    def quality_qr_svg():
        request_id_value = request.args.get("request_id", "").strip()
        query_params = {}
        if request_id_value.isdigit():
            query_params["entry.123456789"] = request_id_value

        if query_params:
            quality_url = f"{QUALITY_FORM_URL}&{urlencode(query_params)}"
        else:
            quality_url = QUALITY_FORM_URL

        image_io = generate_qr_code(quality_url)
        return send_file(image_io, mimetype="image/svg+xml")

    @app.route("/feedback/new", methods=["GET", "POST"])
    def feedback_new():
        if request.method == "POST":
            rating_value = request.form.get("rating", "").strip()
            feedback_text = request.form.get("feedback_text", "").strip()
            request_id_value = request.form.get("request_id", "").strip()

            if not rating_value.isdigit() or int(rating_value) < 1 or int(rating_value) > 5:
                flash("Оценка должна быть числом от 1 до 5.", "warning")
                return render_template("feedback_form.html")

            request_id = int(request_id_value) if request_id_value.isdigit() else None
            if request_id is not None and db.session.get(Request, request_id) is None:
                flash("Заявка не найдена, отзыв сохранен без привязки.", "info")
                request_id = None

            db.session.add(
                FeedbackReview(
                    request_id=request_id,
                    rating=int(rating_value),
                    feedback_text=feedback_text or None,
                )
            )
            if _safe_commit("Спасибо, отзыв сохранен.", "Не удалось сохранить отзыв."):
                return redirect(url_for("feedback_new"))

        return render_template("feedback_form.html")

    @app.errorhandler(403)
    def forbidden(_error):
        return render_template("error.html", code=403, message="Доступ запрещен."), 403

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("error.html", code=404, message="Страница не найдена."), 404

    @app.errorhandler(500)
    def server_error(_error):
        db.session.rollback()
        return (
            render_template(
                "error.html",
                code=500,
                message="Внутренняя ошибка сервера. Повторите действие позже.",
            ),
            500,
        )
