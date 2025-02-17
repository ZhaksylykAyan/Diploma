# Generated by Django 5.1.3 on 2024-11-28 17:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='diploma',
            name='description',
        ),
        migrations.AddField(
            model_name='diploma',
            name='skills',
            field=models.ManyToManyField(related_name='diplomas', to='users.skill'),
        ),
        migrations.AddField(
            model_name='diploma',
            name='teacher',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='diplomas', to='users.teacher'),
        ),
        migrations.AlterField(
            model_name='diploma',
            name='title',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='skill',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('students', models.ManyToManyField(related_name='teams', to='users.student')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='managed_teams', to='users.teacher')),
            ],
        ),
        migrations.AddField(
            model_name='diploma',
            name='team',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='diplomas', to='users.team'),
        ),
        migrations.AddField(
            model_name='teacher',
            name='teams',
            field=models.ManyToManyField(related_name='teachers_list', to='users.team'),
        ),
        migrations.AlterField(
            model_name='student',
            name='team',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='members', to='users.team'),
        ),
        migrations.DeleteModel(
            name='StudentTeam',
        ),
    ]
