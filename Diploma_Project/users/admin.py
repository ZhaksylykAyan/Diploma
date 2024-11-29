from django.contrib import admin
from .models import Skill, Student, Teacher, Team, Diploma
from django.core.exceptions import ValidationError
from .forms import TeamAdminForm

class SkillAdmin(admin.ModelAdmin):
    list_display = ['name']


class StudentAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email']
    filter_horizontal = ('skills',)  # Позволяет выбирать несколько скиллов


class TeacherAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email']
    filter_horizontal = ('skills',)  # Позволяет выбирать несколько скиллов


class TeamAdmin(admin.ModelAdmin):
    form = TeamAdminForm
    list_display = ('name', 'teacher')
    filter_horizontal = ('students', 'skills')
    search_fields = ('name',)


class DiplomaAdmin(admin.ModelAdmin):
    list_display = ['title', 'team', 'teacher']
    filter_horizontal = ('skills',)  # Позволяет выбрать скиллы для диплома


admin.site.register(Skill, SkillAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Diploma, DiplomaAdmin)