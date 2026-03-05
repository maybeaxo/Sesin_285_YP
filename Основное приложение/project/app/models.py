from __future__ import annotations

from datetime import date, datetime

from flask_login import UserMixin

from .extensions import db


REQUEST_STATUSES = ("open", "in_progress", "waiting_parts", "completed")


class Role(db.Model):
    __tablename__ = "roles"

    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False)

    users = db.relationship("User", back_populates="role", lazy="dynamic")


class Master(db.Model):
    __tablename__ = "masters"

    master_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    specialization = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30), nullable=False)

    user = db.relationship("User", back_populates="master", uselist=False)
    assigned_requests = db.relationship("Request", back_populates="master", lazy="dynamic")
    collaboration_requests = db.relationship("RequestCollaborator", back_populates="master", lazy="dynamic")


class User(UserMixin, db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(60), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.role_id"), nullable=False)
    master_id = db.Column(db.Integer, db.ForeignKey("masters.master_id"), nullable=True)

    role = db.relationship("Role", back_populates="users")
    master = db.relationship("Master", back_populates="user")
    comments = db.relationship("RequestComment", back_populates="user", lazy="dynamic")
    notifications = db.relationship("StatusNotification", back_populates="user", lazy="dynamic")

    def get_id(self) -> str:
        return str(self.user_id)

    @property
    def role_name(self) -> str:
        if self.role is None:
            return ""
        return self.role.role_name


class Client(db.Model):
    __tablename__ = "clients"

    client_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    address = db.Column(db.String(255), nullable=True)

    equipment_items = db.relationship("Equipment", back_populates="client", lazy="dynamic")


class Equipment(db.Model):
    __tablename__ = "equipment"

    equipment_id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(120), nullable=False)
    serial_number = db.Column(db.String(80), nullable=False, unique=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.client_id"), nullable=False)
    equipment_type = db.Column(db.String(80), nullable=False)

    client = db.relationship("Client", back_populates="equipment_items")
    requests = db.relationship("Request", back_populates="equipment", lazy="dynamic")


class FaultType(db.Model):
    __tablename__ = "fault_types"

    fault_type_id = db.Column(db.Integer, primary_key=True)
    fault_name = db.Column(db.String(120), nullable=False, unique=True)

    request_details = db.relationship("RequestDetail", back_populates="fault_type", lazy="dynamic")


class Request(db.Model):
    __tablename__ = "requests"
    __table_args__ = (
        db.CheckConstraint(
            "status IN ('open', 'in_progress', 'waiting_parts', 'completed')",
            name="chk_request_status",
        ),
    )

    request_id = db.Column(db.Integer, primary_key=True)
    create_date = db.Column(db.Date, nullable=False, default=date.today)
    description = db.Column(db.Text, nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey("equipment.equipment_id"), nullable=False)
    master_id = db.Column(db.Integer, db.ForeignKey("masters.master_id"), nullable=True)
    status = db.Column(db.String(30), nullable=False, default="open")
    completion_date = db.Column(db.Date, nullable=True)
    deadline_date = db.Column(db.Date, nullable=True)
    customer_approved_extension = db.Column(db.Boolean, nullable=False, default=False)

    equipment = db.relationship("Equipment", back_populates="requests")
    master = db.relationship("Master", back_populates="assigned_requests")
    details = db.relationship("RequestDetail", back_populates="request", cascade="all, delete-orphan")
    comments = db.relationship("RequestComment", back_populates="request", cascade="all, delete-orphan")
    ordered_parts = db.relationship("OrderedPart", back_populates="request", cascade="all, delete-orphan")
    notifications = db.relationship("StatusNotification", back_populates="request", cascade="all, delete-orphan")
    collaborators = db.relationship("RequestCollaborator", back_populates="request", cascade="all, delete-orphan")
    feedback_reviews = db.relationship("FeedbackReview", back_populates="request", cascade="all, delete-orphan")


class RequestDetail(db.Model):
    __tablename__ = "request_details"
    __table_args__ = (
        db.UniqueConstraint("request_id", "fault_type_id", name="uq_request_fault"),
    )

    detail_id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("requests.request_id"), nullable=False)
    fault_type_id = db.Column(db.Integer, db.ForeignKey("fault_types.fault_type_id"), nullable=False)

    request = db.relationship("Request", back_populates="details")
    fault_type = db.relationship("FaultType", back_populates="request_details")


class RequestComment(db.Model):
    __tablename__ = "request_comments"

    comment_id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("requests.request_id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    comment_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    request = db.relationship("Request", back_populates="comments")
    user = db.relationship("User", back_populates="comments")


class OrderedPart(db.Model):
    __tablename__ = "ordered_parts"
    __table_args__ = (
        db.CheckConstraint("quantity > 0", name="chk_part_quantity"),
    )

    part_id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("requests.request_id"), nullable=False)
    part_name = db.Column(db.String(150), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.String(255), nullable=True)
    ordered_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    request = db.relationship("Request", back_populates="ordered_parts")


class StatusNotification(db.Model):
    __tablename__ = "status_notifications"

    notification_id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("requests.request_id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    old_status = db.Column(db.String(30), nullable=False)
    new_status = db.Column(db.String(30), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    request = db.relationship("Request", back_populates="notifications")
    user = db.relationship("User", back_populates="notifications")


class RequestCollaborator(db.Model):
    __tablename__ = "request_collaborators"
    __table_args__ = (
        db.UniqueConstraint("request_id", "master_id", name="uq_request_master_collab"),
    )

    collaboration_id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("requests.request_id"), nullable=False)
    master_id = db.Column(db.Integer, db.ForeignKey("masters.master_id"), nullable=False)
    added_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    request = db.relationship("Request", back_populates="collaborators")
    master = db.relationship("Master", back_populates="collaboration_requests")


class FeedbackReview(db.Model):
    __tablename__ = "feedback_reviews"
    __table_args__ = (
        db.CheckConstraint("rating >= 1 AND rating <= 5", name="chk_feedback_rating"),
    )

    review_id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("requests.request_id"), nullable=True)
    rating = db.Column(db.Integer, nullable=False)
    feedback_text = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    request = db.relationship("Request", back_populates="feedback_reviews")
