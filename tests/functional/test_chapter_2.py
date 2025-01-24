def test_request_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Microblog" in response.data
    assert b"Hi," in response.data

    response = client.get("/index")
    assert response.status_code == 200
    assert b"Microblog" in response.data
    assert b"Hi," in response.data
