# Generated by Django 5.0.1 on 2024-02-09 23:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loopers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='caddy',
            name='change_email_key',
            field=models.CharField(default=1, max_length=255),
        ),
    ]