# Generated by Django 5.1.3 on 2024-11-28 17:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_remove_diploma_description_diploma_skills_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='diploma',
            name='team',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='diplomas', to='users.team'),
        ),
    ]
