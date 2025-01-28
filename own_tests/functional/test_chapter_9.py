def test_explore_login_required_user(client):
    response = client.get("/explore")
    assert response.status_code == 302

    response = client.get("/explore", follow_redirects=True)
    assert response.status_code == 200
    assert len(response.history) == 1
    assert response.request.path == "/login"


def test_explore_authentication(client):
    response = client.get("/explore", follow_redirects=True)
    assert response.status_code == 200
    assert "/login" in response.request.path
    next_url = response.request.args.get("next")

    assert next_url == "/explore"

    response = client.post('/login',
                           data={
                               "username": "Neksper",
                               "password": "1234",
                               "remember_me": True,
                               "next": next_url
                           },
                           follow_redirects=True)
    assert response.status_code == 200
    assert b"Explore" in response.data
