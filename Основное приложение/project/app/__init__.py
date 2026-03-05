from __future__ import annotations

from flask import Flask

from .config import Config
from .extensions import db, login_manager
from .models import User
from .seeds import seed_reference_data


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    login_manager.init_app(app)

    from .routes import register_routes

    register_routes(app)

    with app.app_context():
        db.create_all()
        if not app.config.get("TESTING", False):
            seed_reference_data()

    return app
