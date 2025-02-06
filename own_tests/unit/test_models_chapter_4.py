from app.models import Post


def test_new_user(user):
    assert user.username == "user_unique"
    assert user.email == "email@example.com"
    assert user.id is None
    assert user.password_hash is None


def test_new_post(user):
    post = Post(body="Hello my name is user!", author=user)
    assert post.body == "Hello my name is user!"
    assert post.author == user
    assert post.id is None
    assert post.user_id is None
