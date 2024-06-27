from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

from loopers.models import Caddy

class CaddyMaster(Caddy):
    class Meta:
        proxy: True
        permissions = [("can_create_teetimes", "Can create Teetimes")]

class CaddyShack(models.Model):
    caddy_shack_title = models.CharField(max_length=100)
    caddy_master = models.ForeignKey(CaddyMaster, on_delete=models.CASCADE)
    caddys = models.ManyToManyField(User, related_name="caddys_in_shack")

    def __str__(self):
        return self.caddy_shack_title


def get_sentinel_user():
    return get_user_model().objects.get_or_create(username="deleted_caddy")[0]

class TeeTime(models.Model):
    golfers = models.CharField(max_length=100)
    caddy = models.ForeignKey(User, on_delete=models.SET(get_sentinel_user))
    time = models.DateTimeField()
    position = models.IntegerField(null=True, blank=True)
    flight = models.CharField(max_length=4, blank=True)
    caddy_shack = models.ForeignKey(CaddyShack, on_delete=models.CASCADE)

    def __str__(self) -> str:
        time_str = self.time.strftime(" %I:%M %p on %m/%d/%Y")
        golfers_and_time = self.golfers + time_str
        return golfers_and_time 

    def get_absolute_url(self):
        return reverse("caddymaster:teetime-detail", kwargs={"pk": self.pk})
