import os

import pytest

from app import app, db
from app.models import User


@pytest.fixture(scope="session")
def conf_app():
    app.config.update(
        {"TESTING": True}
    )
    app.config.update(
        {'WTF_CSRF_ENABLED': False}
    )

    yield app


@pytest.fixture(scope="session")
def client(conf_app):
    with conf_app.app_context():
        db.create_all()

        yield conf_app.test_client()

        db.session.remove()
        db.drop_all()
        db.engine.dispose()

    if os.path.exists(conf_app.config["SQLALCHEMY_DATABASE_URI"].split("///")[1]):
        os.remove(conf_app.config["SQLALCHEMY_DATABASE_URI"].rsplit("///")[1])


@pytest.fixture(scope="module")
def user():
    yield User(username="user", email="email@example.com")

# @pytest.fixture()
# def runner(conf_app):
#     return app.test_cli_runner()
