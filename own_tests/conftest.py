import os
import shutil

import pytest

from config import Config
from app import create_app, db
from app.models import User
from app.search import create_whoosh_dir


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    WTF_CSRF_ENABLED = False
    WHOOSH_INDEX_DIR = "test"


@pytest.fixture(scope="session", autouse=True)
def delete_logs():
    if os.path.exists("logs"):
        shutil.rmtree("logs")


@pytest.fixture(scope="module")
def conf_app(delete_logs):
    app = create_app(TestConfig)
    yield app

    if os.path.exists(app.whoosh_dir):
        shutil.rmtree(app.whoosh_dir)


@pytest.fixture(scope="module")
def client(conf_app):
    with conf_app.app_context():
        db.create_all()

        yield conf_app.test_client()

        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture(scope="module")
def user():
    yield User(username="user_unique", email="email@example.com")

# @pytest.fixture()
# def runner(conf_app):
#     return app.test_cli_runner()
