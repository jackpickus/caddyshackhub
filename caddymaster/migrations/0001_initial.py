# Generated by Django 5.0.1 on 2024-02-13 04:54

import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CaddyMaster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_validated', models.BooleanField(default=False)),
                ('change_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CaddyShack',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('caddy_shack_title', models.CharField(max_length=100)),
                ('date', models.DateField(default=datetime.date.today)),
                ('golfer_groups', models.JSONField(null=True)),
                ('caddy_master', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='caddymaster.caddymaster')),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
    ]
