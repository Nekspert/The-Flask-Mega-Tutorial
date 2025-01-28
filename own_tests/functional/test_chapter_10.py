def test_reset_password_request(client):
    response = client.get("/reset_password_request")
    assert response.status_code == 200
    assert b"<h1>Reset Password</h1>" in response.data


def test_reset_password_with_invalid_token(client):
    response = client.get("/reset_password/1")
    assert response.status_code == 302

    response = client.get("/reset_password/1", follow_redirects=True)
    assert response.status_code == 200
    assert len(response.history) == 2
    paths = [resp.request.path for resp in response.history]
    assert "/reset_password/1" == paths[0] and "/index" == paths[1]
    assert response.request.path == "/login"
