from __future__ import annotations

from datetime import date, timedelta

from werkzeug.security import generate_password_hash

from .extensions import db
from .models import (
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


def seed_reference_data() -> None:
    role_names = ["admin", "operator", "master", "manager"]
    for role_name in role_names:
        if Role.query.filter_by(role_name=role_name).first() is None:
            db.session.add(Role(role_name=role_name))

    fault_names = [
        "Утечка хладагента",
        "Неисправность компрессора",
        "Сбой электроники",
        "Засорение фильтра",
        "Шум и вибрация",
        "Перегрев платы управления",
        "Неисправность датчика температуры",
    ]
    for fault_name in fault_names:
        if FaultType.query.filter_by(fault_name=fault_name).first() is None:
            db.session.add(FaultType(fault_name=fault_name))

    masters_data = [
        ("Иванов Сергей Петрович", "Кондиционеры", "+7-900-000-11-01"),
        ("Петрова Ольга Викторовна", "Вентиляция", "+7-900-000-11-02"),
        ("Сидоров Алексей Николаевич", "Отопление", "+7-900-000-11-03"),
        ("Артемьев Денис Павлович", "Электроника", "+7-900-000-11-04"),
    ]
    for full_name, specialization, phone in masters_data:
        if Master.query.filter_by(phone=phone).first() is None:
            db.session.add(
                Master(
                    full_name=full_name,
                    specialization=specialization,
                    phone=phone,
                )
            )

    db.session.flush()

    role_map = {role.role_name: role for role in Role.query.all()}
    master_map = {master.phone: master for master in Master.query.all()}

    users_data = [
        ("admin", "admin123", role_map["admin"], None),
        ("operator", "operator123", role_map["operator"], None),
        ("master", "master123", role_map["master"], master_map.get("+7-900-000-11-01")),
        ("manager", "manager123", role_map["manager"], master_map.get("+7-900-000-11-02")),
    ]
    for login, password, role, master in users_data:
        if User.query.filter_by(login=login).first() is None:
            db.session.add(
                User(
                    login=login,
                    password_hash=generate_password_hash(password),
                    role=role,
                    master=master,
                )
            )

    clients_data = [
        ("Клиент Демо", "+7-900-123-45-67", "demo@example.com", "Екатеринбург, ул. Пример, 1"),
        ("Смирнов Дмитрий Олегович", "+7-912-101-00-01", "smirnov@example.com", "Екатеринбург, ул. Щорса, 15"),
        ("Крылова Алина Сергеевна", "+7-912-101-00-02", "krylova@example.com", "Екатеринбург, ул. Луначарского, 12"),
        ("ООО АльфаСтрой", "+7-912-101-00-03", "office@alfastroy.ru", "Екатеринбург, ул. Машинная, 38"),
        ("ПАО СеверТех", "+7-912-101-00-04", "support@severtech.ru", "Екатеринбург, ул. Куйбышева, 44"),
        ("ИП Лаврентьев", "+7-912-101-00-05", "lavr@example.com", "Екатеринбург, ул. Белинского, 66"),
        ("Медцентр Вектор", "+7-912-101-00-06", "service@vectormed.ru", "Екатеринбург, ул. Репина, 91"),
        ("ТЦ Орион", "+7-912-101-00-07", "tech@orionmall.ru", "Екатеринбург, ул. Вайнера, 9"),
    ]
    for full_name, phone, email, address in clients_data:
        if Client.query.filter_by(phone=phone).first() is None:
            db.session.add(
                Client(
                    full_name=full_name,
                    phone=phone,
                    email=email,
                    address=address,
                )
            )

    db.session.flush()

    client_map = {client.phone: client for client in Client.query.all()}

    equipment_data = [
        ("Кондиционер", "Daikin FTXM35", "SN-DEMO-001", "+7-900-123-45-67"),
        ("Кондиционер", "Mitsubishi Electric MSZ-LN35", "SN-EKB-1001", "+7-912-101-00-01"),
        ("Вентиляция", "Systemair SAVE VTR 300", "SN-EKB-1002", "+7-912-101-00-02"),
        ("Тепловой насос", "Viessmann Vitocal 100", "SN-EKB-1003", "+7-912-101-00-03"),
        ("Кондиционер", "Ballu BSVP-18HN1", "SN-EKB-1004", "+7-912-101-00-04"),
        ("Вентиляция", "Komfovent Domekt R 400", "SN-EKB-1005", "+7-912-101-00-05"),
        ("Кондиционер", "LG Deluxe Pro", "SN-EKB-1006", "+7-912-101-00-06"),
        ("Отопление", "Baxi Luna 3", "SN-EKB-1007", "+7-912-101-00-07"),
        ("Кондиционер", "Toshiba Shorai Edge", "SN-EKB-1008", "+7-912-101-00-03"),
        ("Кондиционер", "Haier Flexis", "SN-EKB-1009", "+7-912-101-00-02"),
    ]
    for equipment_type, model, serial_number, client_phone in equipment_data:
        if Equipment.query.filter_by(serial_number=serial_number).first() is not None:
            continue
        client = client_map.get(client_phone)
        if client is None:
            continue
        db.session.add(
            Equipment(
                model=model,
                serial_number=serial_number,
                equipment_type=equipment_type,
                client_id=client.client_id,
            )
        )

    db.session.flush()

    equipment_map = {equipment.serial_number: equipment for equipment in Equipment.query.all()}

    today = date.today()
    requests_data = [
        ("SN-DEMO-001", "Периодически отключается при запуске", "in_progress", 7, 2, None, "+7-900-000-11-01"),
        ("SN-EKB-1001", "Слабое охлаждение в дневное время", "completed", 16, 10, 8, "+7-900-000-11-01"),
        ("SN-EKB-1002", "Посторонний шум в приточной установке", "waiting_parts", 10, 4, None, "+7-900-000-11-02"),
        ("SN-EKB-1003", "Не запускается наружный блок", "in_progress", 6, 3, None, "+7-900-000-11-04"),
        ("SN-EKB-1004", "Ошибка на дисплее E7", "open", 3, 5, None, "+7-900-000-11-01"),
        ("SN-EKB-1005", "Вентиляция не выходит на номинальную мощность", "completed", 14, 7, 5, "+7-900-000-11-02"),
        ("SN-EKB-1006", "Запах гари при работе", "waiting_parts", 8, 2, None, "+7-900-000-11-04"),
        ("SN-EKB-1007", "Падение давления в отопительном контуре", "in_progress", 5, 4, None, "+7-900-000-11-03"),
        ("SN-EKB-1008", "Срабатывает защита компрессора", "completed", 12, 6, 4, "+7-900-000-11-01"),
        ("SN-EKB-1009", "Не реагирует на пульт управления", "open", 2, 6, None, "+7-900-000-11-04"),
    ]

    for serial_number, description, status, created_days_ago, deadline_days_from_create, completed_after_days, master_phone in requests_data:
        equipment = equipment_map.get(serial_number)
        master = master_map.get(master_phone)
        if equipment is None:
            continue

        exists = Request.query.filter_by(
            equipment_id=equipment.equipment_id,
            description=description,
        ).first()
        if exists is not None:
            continue

        create_date = today - timedelta(days=created_days_ago)
        deadline_date = create_date + timedelta(days=deadline_days_from_create)
        completion_date = None
        if completed_after_days is not None:
            completion_date = create_date + timedelta(days=completed_after_days)

        db.session.add(
            Request(
                create_date=create_date,
                description=description,
                equipment_id=equipment.equipment_id,
                master_id=master.master_id if master else None,
                status=status,
                completion_date=completion_date,
                deadline_date=deadline_date,
                customer_approved_extension=status == "waiting_parts",
            )
        )

    db.session.flush()

    all_faults = FaultType.query.order_by(FaultType.fault_type_id).all()
    all_requests = Request.query.order_by(Request.request_id).all()

    if RequestDetail.query.count() < len(all_requests):
        for index, request_item in enumerate(all_requests):
            if request_item.details:
                continue
            first_fault = all_faults[index % len(all_faults)]
            db.session.add(
                RequestDetail(
                    request_id=request_item.request_id,
                    fault_type_id=first_fault.fault_type_id,
                )
            )
            if request_item.status in {"completed", "waiting_parts"} and len(all_faults) > 1:
                second_fault = all_faults[(index + 2) % len(all_faults)]
                if second_fault.fault_type_id != first_fault.fault_type_id:
                    db.session.add(
                        RequestDetail(
                            request_id=request_item.request_id,
                            fault_type_id=second_fault.fault_type_id,
                        )
                    )

    masters = Master.query.order_by(Master.master_id).all()
    for request_item in all_requests:
        if request_item.master_id is None or len(masters) < 2:
            continue
        if request_item.status not in {"in_progress", "waiting_parts"}:
            continue
        has_collaborator = RequestCollaborator.query.filter_by(request_id=request_item.request_id).first()
        if has_collaborator is not None:
            continue
        second_master = next((m for m in masters if m.master_id != request_item.master_id), None)
        if second_master is None:
            continue
        db.session.add(
            RequestCollaborator(
                request_id=request_item.request_id,
                master_id=second_master.master_id,
            )
        )

    user_map = {user.login: user for user in User.query.all()}

    for request_item in all_requests:
        author = user_map.get("master") or user_map.get("operator")
        reviewer = user_map.get("manager") or user_map.get("admin")
        existing_comments = RequestComment.query.filter_by(request_id=request_item.request_id).count()
        if author and existing_comments == 0:
            db.session.add(
                RequestComment(
                    request_id=request_item.request_id,
                    user_id=author.user_id,
                    comment_text="Проведена диагностика, определены первичные причины неисправности.",
                )
            )
            existing_comments += 1
        if reviewer and request_item.status in {"waiting_parts", "completed"} and existing_comments < 2:
            db.session.add(
                RequestComment(
                    request_id=request_item.request_id,
                    user_id=reviewer.user_id,
                    comment_text="Контроль качества выполнен, требуется соблюдение сроков выполнения.",
                )
            )

    for request_item in all_requests:
        if request_item.status not in {"waiting_parts", "completed"}:
            continue
        existing_parts = OrderedPart.query.filter_by(request_id=request_item.request_id).count()
        if existing_parts >= 1:
            continue
        db.session.add(
            OrderedPart(
                request_id=request_item.request_id,
                part_name="Датчик температуры",
                quantity=1,
                notes="Поставка 2-3 рабочих дня",
            )
        )

    actor = user_map.get("manager") or user_map.get("admin")
    if actor:
        for request_item in all_requests:
            if request_item.status == "open":
                continue
            existing_notification = StatusNotification.query.filter_by(
                request_id=request_item.request_id
            ).first()
            if existing_notification is not None:
                continue
            db.session.add(
                StatusNotification(
                    request_id=request_item.request_id,
                    user_id=actor.user_id,
                    old_status="open",
                    new_status=request_item.status,
                    message=(
                        f"Заявка №{request_item.request_id}: "
                        f"статус обновлен до '{request_item.status}'."
                    ),
                )
            )

    if FeedbackReview.query.count() == 0:
        completed_requests = Request.query.filter_by(status="completed").all()
        for idx, request_item in enumerate(completed_requests):
            rating = 5 if idx % 2 == 0 else 4
            db.session.add(
                FeedbackReview(
                    request_id=request_item.request_id,
                    rating=rating,
                    feedback_text="Работа выполнена качественно и в согласованный срок.",
                )
            )

    db.session.commit()
