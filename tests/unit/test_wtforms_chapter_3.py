from app import app, forms


def test_valid_login_form():
    with app.app_context():
        form = forms.LoginForm(username="user", password="password", remember_me=True)
    assert form.validate() is True
    assert len(form.errors) == 0


def test_missing_username():
    with app.app_context():
        form = forms.LoginForm(username="", password="password", remember_me=True)
    assert form.validate() is False
    assert len(form.errors) == 1 and {"username": ["This field is required."]} == form.errors
    assert ['This field is required.'] == form.username.errors


def test_missing_password():
    with app.app_context():
        form = forms.LoginForm(username="user", password="", rememner_me=True)
    assert form.validate() is False
    assert len(form.errors) == 1 and {"password": ["This field is required."]} == form.errors
    assert ["This field is required."] == form.errors["password"]


def test_missing_both_fields():
    with app.app_context():
        form = forms.LoginForm(username="", password="")
    assert form.validate() is False
    assert len(form.errors) == 2
    assert "username" in form.errors
    assert "password" in form.errors
    assert ["This field is required."] == form.errors["username"]
    assert ["This field is required."] == form.errors["password"]


def test_remember_me_field():
    with app.app_context():
        form = forms.LoginForm(username="user", password="password", remember_me=True)
    assert form.validate() is True
    assert form.remember_me.data is True
    assert len(form.errors) == 0

    with app.app_context():
        form = forms.LoginForm(username="user", password="password", remember_me=False)
    assert form.validate() is True
    assert form.remember_me.data is False
    assert len(form.errors) == 0


def test_submit_field():
    with app.app_context():
        form = forms.LoginForm(username="user", password="password", submit=True)
        # The submit filed doesn't have any validators, so it shouldn't affect validation

    assert form.validate() is True
    assert form.submit.data is True
    assert len(form.errors) == 0
