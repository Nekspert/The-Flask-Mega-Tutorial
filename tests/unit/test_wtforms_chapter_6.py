from app import app, forms


def test_valid_edit_profile_form():
    with app.app_context():
        form = forms.EditProfileForm(username="user2", about_me="")
    assert form.validate() is True
    assert len(form.errors) == 0


def test_missing_username_form():
    with app.app_context():
        form = forms.EditProfileForm(username="", about_me="")
    assert form.validate() is False
    assert len(form.errors) == 1


def test_too_match_about_me_form():
    with app.app_context():
        form = forms.EditProfileForm(username="user2", about_me="1" * 257)
    assert form.validate() is False
    assert len(form.errors) == 1
