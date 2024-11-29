from django.urls import path
from . import views

urlpatterns = [
    path('student/profile/', views.StudentProfileView.as_view(), name='student_profile_api'),
    path('teacher/profile/', views.TeacherProfileView.as_view(), name='teacher_profile_api'),
]