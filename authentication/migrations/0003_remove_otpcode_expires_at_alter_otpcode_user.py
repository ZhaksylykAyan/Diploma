# Generated by Django 5.1.6 on 2025-02-11 15:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_otpcode'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='otpcode',
            name='expires_at',
        ),
        migrations.AlterField(
            model_name='otpcode',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='otp', to=settings.AUTH_USER_MODEL),
        ),
    ]
