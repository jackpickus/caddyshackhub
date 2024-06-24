from django.contrib import admin

from .models import CaddyMaster, TeeTime, CaddyShack

admin.site.register(CaddyMaster)
admin.site.register(TeeTime)
admin.site.register(CaddyShack)