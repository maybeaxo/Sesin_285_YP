"""Импорт данных из CSV-файлов в базу service_desk.db.

Ожидаемые файлы в папке import_data/:
- clients.csv
- equipment.csv
- masters.csv
- fault_types.csv
"""

from __future__ import annotations

import csv
from pathlib import Path

from app import create_app
from app.extensions import db
from app.models import Client, Equipment, FaultType, Master


def import_clients(path: Path):
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            if not row.get("phone"):
                continue
            exists = Client.query.filter_by(phone=row["phone"]).first()
            if exists:
                continue
            db.session.add(
                Client(
                    full_name=row.get("full_name", ""),
                    phone=row.get("phone", ""),
                    email=row.get("email") or None,
                    address=row.get("address") or None,
                )
            )


def import_masters(path: Path):
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            if not row.get("phone"):
                continue
            exists = Master.query.filter_by(phone=row["phone"]).first()
            if exists:
                continue
            db.session.add(
                Master(
                    full_name=row.get("full_name", ""),
                    specialization=row.get("specialization", ""),
                    phone=row.get("phone", ""),
                )
            )


def import_fault_types(path: Path):
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            fault_name = row.get("fault_name", "").strip()
            if not fault_name:
                continue
            exists = FaultType.query.filter_by(fault_name=fault_name).first()
            if exists:
                continue
            db.session.add(FaultType(fault_name=fault_name))


def import_equipment(path: Path):
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            serial_number = row.get("serial_number", "").strip()
            client_phone = row.get("client_phone", "").strip()
            if not serial_number or not client_phone:
                continue
            exists = Equipment.query.filter_by(serial_number=serial_number).first()
            client = Client.query.filter_by(phone=client_phone).first()
            if exists or client is None:
                continue
            db.session.add(
                Equipment(
                    model=row.get("model", ""),
                    serial_number=serial_number,
                    equipment_type=row.get("equipment_type", ""),
                    client_id=client.client_id,
                )
            )


def main():
    app = create_app()
    import_dir = Path(__file__).resolve().parent.parent / "import_data"

    with app.app_context():
        import_clients(import_dir / "clients.csv")
        import_masters(import_dir / "masters.csv")
        import_fault_types(import_dir / "fault_types.csv")
        db.session.flush()
        import_equipment(import_dir / "equipment.csv")
        db.session.commit()

    print("Импорт завершен.")


if __name__ == "__main__":
    main()
