import pytest
from microblog import app
from app.models import User


@pytest.fixture(scope="module")
def conf_app():
    app.config.update(
        {"TESTING": True}
    )
    app.config.update(
        {'WTF_CSRF_ENABLED': False}
    )

    yield app


@pytest.fixture(scope="module")
def client(conf_app):
    return conf_app.test_client()


@pytest.fixture(scope="module")
def user():
    yield User(username="user", email="email@example.com")

# @pytest.fixture()
# def runner(conf_app):
#     return app.test_cli_runner()
