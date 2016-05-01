from django.contrib.auth.models import User, Group
from rest_framework import serializers
from flow.models import Course, Teacher, Student, AttendedCourse, CourseRating


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class CourseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Course
        fields = ('url', 'name', 'image', 'teachers')


class TeacherSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Teacher
        fields = ('url', 'first_name', 'last_name', 'image', 'courses')


class StudentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Student
        fields = ('url', 'username', 'first_name', 'last_name', 'registered_date')


class AttendedCourseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AttendedCourse
        fields = ('url', 'course', 'teacher', 'student', 'clear', 'engaging', 'easy')


class CourseRatingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CourseRating
        fields = ('url', 'course', 'student', 'useful', 'easy', 'liked')
