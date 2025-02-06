from app.models import Post
from app import db


def test_search(user, client):
    with client.application.test_request_context():
        post1 = Post(body="Hi 1", author=user)
        post2 = Post(body="Hi 2", author=user)
        db.session.add(post1)
        db.session.add(post2)
        db.session.commit()

    Post.reindex()

    query, total = Post.search("Hi", 1, 2)
    results = query.all()
    assert total == 2
    assert len(results) == 2
    assert [post1, post2] == results
