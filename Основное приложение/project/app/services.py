from __future__ import annotations

from datetime import date, datetime
from io import BytesIO

import qrcode
import qrcode.image.svg
from sqlalchemy import func

from .extensions import db
from .models import FaultType, Request, RequestDetail


STATUS_LABELS = {
    "open": "Открыта",
    "in_progress": "В процессе",
    "waiting_parts": "Ожидание комплектующих",
    "completed": "Завершена",
}


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def status_label(status: str) -> str:
    return STATUS_LABELS.get(status, status)


def calculate_statistics() -> dict:
    completed_requests = Request.query.filter_by(status="completed").all()
    completed_count = len(completed_requests)

    total_days = 0
    counted = 0
    for req in completed_requests:
        if req.completion_date and req.create_date:
            total_days += (req.completion_date - req.create_date).days
            counted += 1

    average_days = round(total_days / counted, 2) if counted else 0

    fault_rows = (
        db.session.query(FaultType.fault_name, func.count(RequestDetail.detail_id))
        .join(RequestDetail, FaultType.fault_type_id == RequestDetail.fault_type_id)
        .group_by(FaultType.fault_name)
        .order_by(func.count(RequestDetail.detail_id).desc())
        .all()
    )

    fault_stats = [{"fault_name": row[0], "count": row[1]} for row in fault_rows]

    return {
        "completed_count": completed_count,
        "average_completion_days": average_days,
        "fault_stats": fault_stats,
    }


def generate_qr_code(data: str) -> BytesIO:
    image_io = BytesIO()
    image = qrcode.make(data, image_factory=qrcode.image.svg.SvgPathImage)
    image.save(image_io)
    image_io.seek(0)
    return image_io
