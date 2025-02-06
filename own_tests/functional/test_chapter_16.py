from flask_login import current_user

from app import db
from app.models import Post


def test_search_outside_in(client, user):
    post1 = Post(body="Hi 1", author=user)
    post2 = Post(body="Hi 2", author=user)
    db.session.add(post1)
    db.session.add(post2)
    db.session.commit()

    Post.reindex()
    with client.application.test_request_context():
        client.post("/auth/register", follow_redirects=True,
                               data={
                                   "username": "user5",
                                   "email": "user4@example.com",
                                   "password": "1234",
                                   "password2": "1234"
                               })
        client.post("/auth/login", follow_redirects=True,
                    data={
                        "username": "user5",
                        "password": "1234"
                    })
        assert current_user.is_authenticated is True
        response = client.get("/search?q=Hi")

        assert response.status_code == 200
        assert "Hi 1" in response.text
        assert "Hi 2" in response.text
