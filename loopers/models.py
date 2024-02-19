import datetime

from django.db import models
from django.urls import reverse

from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class Caddy(models.Model):
    # one to one because a caddy can only have one user and a user can only be one caddy
    # SET_NULL: the reference to a user will be null
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)

    activation_key = models.CharField(max_length=255, default=1)
    email_validated = models.BooleanField(default=False)
    loop_count = models.IntegerField(default=0)

    # this field is used for when a caddy wants to change their email
    # save the 'new' email here, then once its verified, set the email field
    # in their user object to it
    change_email = models.EmailField(max_length=254, null=True, blank=True)
    change_email_key = models.CharField(max_length=255, null=True, blank=True, default=1)

    friends = models.ManyToManyField("Caddy", symmetrical=False, blank=True)

    def __str__(self):
        return self.user.username


def no_future_loop_date(value):
    today = datetime.date.today()
    if value > today:
        raise ValidationError("Loop date cannot be in the future.")


class Loop(models.Model):
    loop_title = models.CharField(max_length=100)
    date = models.DateField(
        default=datetime.date.today,
        validators=[no_future_loop_date],
    )
    num_loops = models.IntegerField("Number of loops", default=1)
    money = models.IntegerField("Money made")
    notes = models.TextField(blank=True)

    # Foreign Key used because loop can only have one caddy, but caddys can have multiple loops
    # CASCADE: When the reference object is deleted the loop will also be deleted
    caddy = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return self.loop_title

    def get_absolute_url(self):
        return reverse("loopers:loop-detail", kwargs={"pk": self.pk})
