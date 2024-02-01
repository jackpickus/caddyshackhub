from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext_lazy as _

from .models import Loop


class NewUserForm(forms.Form):
    username = forms.CharField(label="Enter Username", min_length=4, max_length=50)
    email = forms.EmailField(label="Enter email")
    password1 = forms.CharField(label="Enter password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data["username"].lower()
        r = User.objects.filter(username=username)
        if r.count():
            raise ValidationError("Username already exists")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        r = User.objects.filter(email=email)
        if r.count():
            raise ValidationError("Email already exists")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match")

        if len(password2) < 8:
            raise ValidationError("Password must be at least 8 characters long")

        contains_special_char = any(not c.isalnum() for c in password2)
        if not contains_special_char:
            raise ValidationError("Password must contain a special character")

        if not any(c.isdigit() for c in password2):
            raise ValidationError("Password must contain a number")

        return password2

    def save(self, commit=True):
        user = User.objects.create_user(
            self.cleaned_data["username"],
            self.cleaned_data["email"],
            self.cleaned_data["password1"],
        )
        return user


class NewLoopForm(forms.ModelForm):
    class Meta:
        model = Loop
        exclude = ["caddy"]
        labels = {
            "num_loops": _("Number of loops"),
        }


class FollowCaddyForm(forms.Form):
    caddy_to_follow = forms.CharField(
        label="Follow other caddys:",
        widget=forms.TextInput(attrs={"placeholder": "username"}),
    )

    def clean_caddy_to_follow(self):
        caddy_to_follow = self.cleaned_data["caddy_to_follow"].lower()
        if not User.objects.filter(username=caddy_to_follow).exists():
            raise ValidationError("Username does not exist")
        return caddy_to_follow


class ChangeEmailForm(forms.Form):
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    new_email = forms.EmailField(label="New email")

    def clean_new_email(self):
        new_email = self.cleaned_data["new_email"].lower()
        r = User.objects.filter(email=new_email)
        if r.count():
            raise ValidationError("Email already in use")
        return new_email