def test_request_register_get(client):
    response = client.get("/register")
    assert response.status_code == 200
    assert b"Register" in response.data
    assert b"Username" in response.data
    assert b"Email" in response.data
    assert b"Password" in response.data
    assert b"Repeat Password" in response.data


def test_request_register_post(client):
    response = client.post("/register", follow_redirects=True,
                           data={
                               "username": "user4",
                               "email": "user4@example.com",
                               "password": "1234",
                               "password2": "1234"
                           })
    assert response.status_code == 200
    assert len(response.history) == 1
    assert response.request.path == "/login"
