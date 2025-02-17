from rest_framework import serializers
from .models import Student, Teacher, Skill, Team, Diploma


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name']
        read_only_fields = ['id', 'name']

class StudentSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True)  # Вложенные скиллы, которые у студента
    team = serializers.StringRelatedField()  # Показываем название команды

    class Meta:
        model = Student
        fields = ['id', 'first_name', 'last_name', 'email', 'skills', 'team']
        read_only_fields = ['first_name', 'last_name', 'email', 'skills', 'team']

class TeacherSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True)
    teams = serializers.StringRelatedField(many=True)

    class Meta:
        model = Teacher
        fields = ['id', 'first_name', 'last_name', 'email', 'skills', 'teams']
        read_only_fields = ['id','first_name', 'last_name', 'email', 'skills', 'teams']


class TeamSerializer(serializers.ModelSerializer):
    students = StudentSerializer(many=True)
    teacher = TeacherSerializer()

    class Meta:
        model = Team
        fields = ['id', 'name', 'students', 'teacher']
        read_only_fields = ['id', 'name', 'students', 'teacher']

    def validate(self, data):
        if len(data['students']) > 4:
            raise serializers.ValidationError("Максимальное количество студентов в команде — 4.")
        if data['teacher'].teams.count() >= 10:
            raise serializers.ValidationError("Учитель не может вести больше 10 команд.")
        return data

from rest_framework import serializers
from .models import Diploma, Skill

class DiplomaSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True)
    team = TeamSerializer()
    teacher = TeacherSerializer()

    class Meta:
        model = Diploma
        fields = ['id', 'title', 'team', 'teacher', 'skills']

    def create(self, validated_data):
        skills_data = validated_data.pop('skills')
        team_data = validated_data.pop('team')
        teacher_data = validated_data.pop('teacher')

        # Создание диплома
        diploma = Diploma.objects.create(**validated_data)
        diploma.skills.set(skills_data)  # Присваиваем скиллы
        diploma.save()

        return diploma