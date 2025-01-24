def test_request_login_get(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Username" in response.data
    assert b"Password" in response.data
    assert b"Remember Me" in response.data


def test_request_login_post(client):
    response = client.post("/login", follow_redirects=True,
                           data={
                               "username": "user",
                               "password": "password",
                               "remember_me": True,
                           }
                           )

    assert response.status_code == 200
    assert len(response.history) == 1
    assert response.request.path == "/login"
