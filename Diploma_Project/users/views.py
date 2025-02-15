from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Student, Teacher
from .serializers import StudentSerializer, TeacherSerializer


class StudentProfileView(generics.RetrieveAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return Student.objects.get(user=self.request.user)

class TeacherProfileView(generics.RetrieveAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return Teacher.objects.get(user=self.request.user)