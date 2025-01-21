def test_request_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Microblog" in response.data
    assert b"Timur" in response.data
    assert b"Rasul says: " in response.data
    assert b"The avengers movie was so cool!" in response.data

    response = client.get("/index")
    assert response.status_code == 200
    assert b"Microblog" in response.data
    assert b"Timur" in response.data
    assert b"Rasul says: " in response.data
    assert b"The avengers movie was so cool!" in response.data
