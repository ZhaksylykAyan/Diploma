from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

# Create your models here.
class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    skills = models.ManyToManyField(Skill, related_name='students')
    team = models.ForeignKey("Team", on_delete=models.SET_NULL, null = True, blank=True,related_name='members')
    diploma = models.OneToOneField('Diploma', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    skills = models.ManyToManyField(Skill, related_name='teachers')
    teams = models.ManyToManyField("Team", blank=True, related_name='teachers_list')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def max_team(self):
        return self.teams.count() >= 10

class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    students = models.ManyToManyField(Student, related_name='teams')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='managed_teams')
    skills = models.ManyToManyField(Skill, related_name='teams', blank=True)

    def __str__(self):
        return self.name

    def clean(self):
        # Проверка на количество студентов
        if self.students.count() > 4:
            raise ValidationError("В команде должно быть не больше 4 студентов.")

    def save(self, *args, **kwargs):
        # Автоматическое добавление скиллов студентов и учителя в команду
        super().save(*args, **kwargs)  # Сохраняем команду
        all_skills = set()
        for student in self.students.all():
            all_skills.update(student.skills.all())
        if self.teacher:
            all_skills.update(self.teacher.skills.all())
        self.skills.set(all_skills)  # Обновляем скиллы команды

class Diploma(models.Model):
    title = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='diploma_team')
    teacher = models.OneToOneField(Team, on_delete=models.CASCADE, default=1 , related_name='diploma_teacher')
    skills = models.ManyToManyField(Skill, related_name='diplomas')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Автоматическое добавление скиллов команды в диплом
        super().save(*args, **kwargs)  # Сохраняем диплом
        if self.team:
            self.skills.set(self.team.skills.all())  # Устанавливаем скиллы команды