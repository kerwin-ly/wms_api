import typing
from flask import Flask

from app import resource


def create_app() -> Flask:
    app = Flask(__name__)

    register_blueprint(app)

    return app


def register_blueprint(flask_app: Flask) -> None:
    flask_app.register_blueprint(resource.blueprint)
