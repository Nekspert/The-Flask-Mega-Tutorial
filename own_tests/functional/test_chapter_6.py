def test_login_required_user(client):
    response = client.get("/user/user")
    assert response.status_code == 302

    response = client.get("/user/user", follow_redirects=True)
    assert response.status_code == 200
    assert len(response.history) == 1
    assert response.request.path == "/auth/login"


def test_login_required_edit_profile(client):
    response = client.get("/edit_profile")
    assert response.status_code == 302

    response = client.get("/edit_profile", follow_redirects=True)
    assert response.status_code == 200
    assert len(response.history) == 1
    assert response.request.path == "/auth/login"
