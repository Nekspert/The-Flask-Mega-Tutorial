from app.auth import forms


def test_valid_register_form(client):
    with client:
        form = forms.RegistrationForm(username="user", email="user@example.com", password="1234", password2="1234")
    assert form.validate() is True
    assert len(form.errors) == 0


def test_missing_username(client):
    with client:
        form = forms.RegistrationForm(email="user@example.com", password="1234", password2="1234")
    assert form.validate() is False
    assert len(form.errors) == 1 and {"username": ["This field is required."]} == form.errors
    assert ["This field is required."] == form.username.errors


def test_missing_email(client):
    with client:
        form = forms.RegistrationForm(username="user", password="1234", password2="1234")
    assert form.validate() is False
    assert len(form.errors) == 1 and {"email": ["This field is required."]} == form.errors
    assert ["This field is required."] == form.email.errors


def test_incorrect_email(client):
    with client:
        form = forms.RegistrationForm(username="user", email="user.com", password="1234", password2="1234")
    assert form.validate() is False
    assert len(form.errors) == 1 and {"email": ["Invalid email address."]} == form.errors
    assert ["Invalid email address."] == form.email.errors


def test_missing_password(client):
    with client.application.test_request_context():
        form = forms.RegistrationForm(username="user", email="user@example.com", password2="1234")
        assert form.validate() is False
    assert len(form.errors) == 2 and {"password": ["This field is required."],
                                      "password2": ["Field must be equal to password."]} == form.errors
    assert ["This field is required."] == form.password.errors
    assert ["Field must be equal to password."] == form.password2.errors


def test_missing_password2(client):
    with client:
        form = forms.RegistrationForm(username="user", email="user@example.com", password="1234")
    assert form.validate() is False
    assert len(form.errors) == 1 and {"password2": ["This field is required."]} == form.errors
    assert ["This field is required."] == form.password2.errors
