from conftest import client


def test_request_hello_world(client):
    response = client.get("/")
    assert b"<h1>Hello World</h1>" in response.data


if __name__ == "__main__":
    import pytest

    pytest.main()
