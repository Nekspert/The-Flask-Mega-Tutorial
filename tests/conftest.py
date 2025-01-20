import pytest
from microblog import app


@pytest.fixture(scope="module")
def conf_app():
    app.config.update(
        {"TESTING": True}
    )
    yield app


@pytest.fixture(scope="module")
def client(conf_app):
    return conf_app.test_client()

# @pytest.fixture()
# def runner(conf_app):
#     return app.test_cli_runner()
