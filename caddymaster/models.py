import datetime

from django.db import models

from loopers.models import Caddy

class CaddyMaster(Caddy):
    class Meta:
        proxy: True
        permissions = [("can_assign_loops", "Can assign loops")]

class CaddyShack(models.Model):
    caddy_shack_title = models.CharField(max_length=100)
    date = models.DateField(default=datetime.date.today)

    caddy_master = models.ForeignKey(CaddyMaster, on_delete=models.CASCADE)
    caddys = models.ManyToManyField(Caddy, blank=True, related_name="caddys_in_shack")
    golfer_groups = models.JSONField(null=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return self.caddy_shack_title

class TeeTime(models.Model):
    golfers = models.JSONField(null=False)
    caddy = models.CharField(max_length=100)
    time = models.DateField(default=datetime.date.today)
    position = models.IntegerField(null=True, blank=True)
    flight = models.CharField(max_length=4, null=True, blank=True)