def test_request_index(client):
    response = client.get("/", follow_redirects=True)
    assert response.status_code == 200
    assert len(response.history) == 1
    assert response.request.path == "/auth/login"

    response = client.get("/index", follow_redirects=True)
    assert response.status_code == 200
    assert len(response.history) == 1
    assert response.request.path == "/auth/login"
