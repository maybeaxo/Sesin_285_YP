from datetime import date

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import (
    Client,
    Equipment,
    FaultType,
    Master,
    Request,
    RequestDetail,
    Role,
    StatusNotification,
    User,
)


@pytest.fixture()
def app():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SECRET_KEY": "test-secret",
        }
    )

    with app.app_context():
        db.create_all()

        roles = {
            name: Role(role_name=name)
            for name in ["admin", "operator", "master", "manager"]
        }
        db.session.add_all(roles.values())

        master = Master(
            full_name="Тестовый Мастер",
            specialization="Кондиционеры",
            phone="+7-900-100-00-01",
        )
        db.session.add(master)

        fault = FaultType(fault_name="Сбой электроники")
        db.session.add(fault)
        db.session.flush()

        users = [
            User(
                login="admin",
                password_hash=generate_password_hash("admin123"),
                role_id=roles["admin"].role_id,
            ),
            User(
                login="operator",
                password_hash=generate_password_hash("operator123"),
                role_id=roles["operator"].role_id,
            ),
            User(
                login="manager",
                password_hash=generate_password_hash("manager123"),
                role_id=roles["manager"].role_id,
            ),
            User(
                login="master",
                password_hash=generate_password_hash("master123"),
                role_id=roles["master"].role_id,
                master_id=master.master_id,
            ),
        ]
        db.session.add_all(users)
        db.session.commit()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def _login(client, login, password):
    return client.post(
        "/login",
        data={"login": login, "password": password},
        follow_redirects=True,
    )


def _create_base_request():
    client = Client(
        full_name="Иван Иванов",
        phone="+7-900-100-00-02",
        email="ivan@example.com",
    )
    db.session.add(client)
    db.session.flush()

    equipment = Equipment(
        model="Mitsubishi MSZ-AP25",
        serial_number="SN-T-001",
        equipment_type="Кондиционер",
        client_id=client.client_id,
    )
    db.session.add(equipment)
    db.session.flush()

    master = Master.query.first()
    req = Request(
        create_date=date.today(),
        description="Не охлаждает",
        equipment_id=equipment.equipment_id,
        master_id=master.master_id,
        status="open",
    )
    db.session.add(req)
    db.session.flush()

    fault = FaultType.query.first()
    db.session.add(RequestDetail(request_id=req.request_id, fault_type_id=fault.fault_type_id))
    db.session.commit()
    return req.request_id


def test_login_success(client):
    response = _login(client, "admin", "admin123")
    assert response.status_code == 200
    assert "Панель управления" in response.text


def test_operator_can_create_request(client, app):
    _login(client, "operator", "operator123")

    with app.app_context():
        fault_id = FaultType.query.first().fault_type_id
        master_id = Master.query.first().master_id

    response = client.post(
        "/requests/new",
        data={
            "create_date": "2026-03-05",
            "description": "Посторонний шум",
            "status": "open",
            "deadline_date": "2026-03-10",
            "client_full_name": "Петров Петр",
            "client_phone": "+7-900-200-00-00",
            "client_email": "petrov@example.com",
            "client_address": "Екатеринбург",
            "equipment_type": "Вентиляция",
            "equipment_model": "Ballu BSVP",
            "serial_number": "SN-NEW-001",
            "master_id": str(master_id),
            "fault_type_ids": str(fault_id),
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Заявка №" in response.text

    with app.app_context():
        assert Request.query.count() == 1
        assert Client.query.count() == 1
        assert Equipment.query.count() == 1
        assert RequestDetail.query.count() == 1


def test_status_change_creates_notification(client, app):
    with app.app_context():
        request_id = _create_base_request()
        master_id = Master.query.first().master_id
        fault_id = FaultType.query.first().fault_type_id

    _login(client, "manager", "manager123")

    response = client.post(
        f"/requests/{request_id}/edit",
        data={
            "description": "Не охлаждает, проверка завершена",
            "status": "completed",
            "master_id": str(master_id),
            "deadline_date": "2026-03-12",
            "customer_approved_extension": "on",
            "fault_type_ids": str(fault_id),
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        req = db.session.get(Request, request_id)
        assert req.status == "completed"
        assert req.completion_date is not None
        notifications = StatusNotification.query.filter_by(request_id=request_id).all()
        assert len(notifications) == 1
        assert notifications[0].old_status == "open"
        assert notifications[0].new_status == "completed"


def test_manager_can_extend_deadline(client, app):
    with app.app_context():
        request_id = _create_base_request()

    _login(client, "manager", "manager123")

    response = client.post(
        f"/requests/{request_id}/extend",
        data={
            "deadline_date": "2026-03-20",
            "customer_approved_extension": "on",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        req = db.session.get(Request, request_id)
        assert req.deadline_date.isoformat() == "2026-03-20"
        assert req.customer_approved_extension is True
        assert req.status == "waiting_parts"


def test_stats_page(client, app):
    with app.app_context():
        request_id = _create_base_request()
        req = db.session.get(Request, request_id)
        req.status = "completed"
        req.create_date = date(2026, 3, 1)
        req.completion_date = date(2026, 3, 5)
        db.session.commit()

    _login(client, "operator", "operator123")
    response = client.get("/stats")

    assert response.status_code == 200
    assert "Количество выполненных заявок" in response.text
    assert "1" in response.text
    assert "4.0" in response.text or "4" in response.text
