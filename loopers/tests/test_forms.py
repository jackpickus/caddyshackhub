import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from loopers.models import Loop
from loopers.forms import NewUserForm, NewLoopForm, FollowCaddyForm, ChangeEmailForm


class NewUserFormTest(TestCase):
    def test_username_label(self):
        form = NewUserForm()
        self.assertTrue(
            # have to test whether the label value is None
            # because even though Django will render the correct label
            # it returns None if the value is not explicitly set.
            form.fields["username"].label is None
            or form.fields["username"].label == "Enter Username"
        )

    def test_email_label(self):
        form = NewUserForm()
        self.assertTrue(
            form.fields["email"].label is None
            or form.fields["email"].label == "Enter email"
        )

    def test_password1_label(self):
        form = NewUserForm()
        self.assertTrue(form.fields["password1"].label == "Enter password")

    def test_password2_label(self):
        form = NewUserForm()
        self.assertTrue(form.fields["password2"].label == "Confirm password")

    def test_password_min_length(self):
        username = "usr1"
        email = "test@test.com"
        password1 = "test&12"
        password2 = "test&12"
        form = NewUserForm(
            data={
                "username": username,
                "email": email,
                "password1": password1,
                "password2": password2,
            }
        )
        self.assertFalse(form.is_valid())

    def test_passwords_match(self):
        username = "usr1"
        email = "test@test.com"
        password1 = "test&234"
        password2 = "test&789"
        form = NewUserForm(
            data={
                "username": username,
                "email": email,
                "password1": password1,
                "password2": password2,
            }
        )
        self.assertFalse(form.is_valid())

    def test_password_has_num(self):
        username = "usr1"
        email = "test@test.com"
        password1 = "test&test"
        password2 = "test&test"
        form = NewUserForm(
            data={
                "username": username,
                "email": email,
                "password1": password1,
                "password2": password2,
            }
        )
        self.assertFalse(form.is_valid())

    def test_password_has_special_char(self):
        username = "usr1"
        email = "test@test.com"
        password1 = "test2test"
        password2 = "test2test"
        form = NewUserForm(
            data={
                "username": username,
                "email": email,
                "password1": password1,
                "password2": password2,
            }
        )
        self.assertFalse(form.is_valid())

    def test_form_is_correct(self):
        username = "user1"
        email = "test@test.com"
        password1 = "test2!test"
        password2 = "test2!test"
        form = NewUserForm(
            data={
                "username": username,
                "email": email,
                "password1": password1,
                "password2": password2,
            }
        )
        self.assertTrue(form.is_valid())


class NewLoopFormTest(TestCase):
    def test_num_loops_label(self):
        form = NewLoopForm()
        self.assertTrue(
            form.fields["num_loops"].label is None
            or form.fields["num_loops"].label == "Number of loops"
        )

    def test_date_in_future(self):
        loop_title = "Test"
        notes = "This is a test note"
        one_day_in_future = datetime.date.today() + datetime.timedelta(days=1)
        form = NewLoopForm(
            data={
                "loop_title": loop_title,
                "date": one_day_in_future,
                "num_loops": 1,
                "money": 60,
                "notes": notes,
            }
        )
        self.assertFalse(form.is_valid())


class FollowCaddyFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create(
            username="test_user", password="Stset01@", email="test@test.com"
        )

    def test_follow_caddy_label(self):
        form = FollowCaddyForm()
        self.assertTrue(
            form.fields["caddy_to_follow"].label is None
            or form.fields["caddy_to_follow"].label == "Follow other caddys:"
        )

    def test_caddy_exists(self):
        user1 = User.objects.get(id=1)
        form = FollowCaddyForm(
            data={
                "caddy_to_follow": user1,
            }
        )
        self.assertTrue(form.is_valid())

    def test_caddy_does_not_exist(self):
        form = FollowCaddyForm(
            data={
                "caddy_to_follow": "non_real_user",
            }
        )
        self.assertFalse(form.is_valid())


class ChangeEmailFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create(
            username="test_user", password="Stset01@", email="test@test.com"
        )

    def test_password_label(self):
        form = ChangeEmailForm()
        self.assertTrue(
            form.fields["password"].label is None
            or form.fields["password"].label == "Password"
        )

    def test_new_email_label(self):
        form = ChangeEmailForm()
        self.assertTrue(
            form.fields["new_email"].label is None
            or form.fields["new_email"].label == "New email"
        )

    def test_email_in_use(self):
        user1 = User.objects.get(id=1)
        form = ChangeEmailForm(
            data={
                "new_email": "test@test.com",
                "password": "Test%456",
            }
        )
        self.assertFalse(form.is_valid())
