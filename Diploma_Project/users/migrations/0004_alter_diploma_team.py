# Generated by Django 5.1.3 on 2024-11-29 12:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_diploma_team'),
    ]

    operations = [
        migrations.AlterField(
            model_name='diploma',
            name='team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='diplomas', to='users.team'),
        ),
    ]
