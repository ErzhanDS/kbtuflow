import requests
import json

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User, Group

from rest_framework import viewsets, filters

from utils.secrets import secrets

from flow.serializers import UserSerializer, GroupSerializer
from flow.serializers import CourseSerializer, TeacherSerializer, StudentSerializer, AttendedCourseSerializer, CourseRatingSerializer
from flow.models import Course, Teacher, Student, AttendedCourse, CourseRating

api_url = secrets.get_secret('kbtu_host')


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('name', 'image', 'teacher__first_name', 'teacher__last_name')


class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('first_name', 'last_name', 'image', 'course__name')


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('username', 'first_name', 'last_name')


class AttendedCourseFilter(filters.FilterSet):
    class Meta:
        model = AttendedCourse
        fields = [
            'course__name',
            'course__image',
            'teacher__first_name',
            'teacher__last_name',
            'teacher__image',
            'student__username',
            'student__first_name',
            'student__last_name',
            'clear',
            'engaging',
            'easy',
        ]


class AttendedCourseViewSet(viewsets.ModelViewSet):
    queryset = AttendedCourse.objects.all()
    serializer_class = AttendedCourseSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = AttendedCourseFilter


class CourseRatingFilter(filters.FilterSet):
    class Meta:
        model = CourseRating
        fields = [
            'course__name',
            'course__image',
            'student__username',
            'student__first_name',
            'student__last_name',
            'useful',
            'easy',
            'liked'
        ]


class CourseRatingViewSet(viewsets.ModelViewSet):
    queryset = CourseRating.objects.all()
    serializer_class = CourseRatingSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = CourseRatingFilter


def index(request):
    return render(request, 'index.html', context={
        'text': 'kbtuflow',
    })


# get request: localhost:1111/register-student?username=13BD02051&password=kbtu2016
def register_student(request):
    username = request.GET.get('username')
    password = request.GET.get('password')
    response = requests.post(api_url + '/api/account/token', data={
        'username': username,
        'password': password,
        'deviceToken': 'YerzhanNurzhan',
        'deviceType': 'Android',
    })
    j = response.json()
    if j.get("UserToken"):
        token = j.get("UserToken")
        student_first_name = j["UserInfo"]["Table"][0]["FirstName"].strip()
        student_last_name = j["UserInfo"]["Table"][0]["LastName"].strip()
        try:
            student = Student.objects.get(username=username)
        except:
            student = Student(
                username=username,
                password=password,
                first_name=student_first_name,
                last_name=student_last_name,
            )
        student.first_name = student_first_name
        student.last_name = student_last_name
        student.password = password
        student.save()
        populate_db(token, student)

    return HttpResponse('Done! de :)')


def populate_db(token, student):
    headers = {
        'Authorization': 'Bearer ' + token,
    }
    j = requests.get(api_url + '/api/schedule', headers=headers).json()
    if j.get("Table"):
        for lesson in j.get("Table"):
            course_name = lesson["courseName"].strip()
            try:
                course = Course.objects.get(name=course_name)
            except:
                course = Course(name=course_name)
                course.save()

            teacher_first_name = lesson["FirstName"].strip()
            teacher_last_name = lesson["LastName"].strip()
            try:
                teacher = Teacher.objects.get(first_name=teacher_first_name, last_name=teacher_last_name)
            except:
                teacher = Teacher(first_name=teacher_first_name, last_name=teacher_last_name)
                teacher.save()

            course.teachers.add(teacher)

            try:
                course_rating = CourseRating.objects.get(course=course, student=student)
            except:
                course_rating = CourseRating(course=course, student=student)
                course_rating.save()

            try:
                attended_course = AttendedCourse.objects.get(course=course, teacher=teacher, student=student)
            except:
                attended_course = AttendedCourse(course=course, teacher=teacher, student=student)
                attended_course.save()


def update_attended_course(request):
    username = request.GET.get('username')
    course_name = request.GET.get('course_name')
    teacher_first_name = request.GET.get('teacher_first_name')
    teacher_last_name = request.GET.get('teacher_last_name')
    clear = request.GET.get('clear')
    engaging = request.GET.get('engaging')
    easy = request.GET.get('easy')
    try:
        course = Course.objects.get(name=course_name)
        teacher = Teacher.objects.get(first_name=teacher_first_name, last_name=teacher_last_name)
        student = Student.objects.get(username=username)
        attended_course = AttendedCourse.objects.get(course=course, teacher=teacher, student=student)
        attended_course.clear = clear
        attended_course.engaging = engaging
        attended_course.easy = easy
        attended_course.save()
    except:
        pass

    return HttpResponse('Done! de :)')


def update_course_rating(request):
    username = request.GET.get('username')
    course_name = request.GET.get('course_name').replace('_', ' ')
    useful = request.GET.get('useful')
    easy = request.GET.get('easy')
    liked = request.GET.get('liked')
    try:
        course = Course.objects.get(name=course_name)
        student = Student.objects.get(username=username)
        course_rating = CourseRating.objects.get(course=course, student=student)
        course_rating.useful = useful
        course_rating.easy = easy
        course_rating.liked = liked
        course_rating.save()
    except:
        pass

    return HttpResponse('Done! de :)')


def get_course_rating(request):
    course_name = request.GET.get('course_name').replace('_', ' ')
    try:
        total = CourseRating.objects.filter(course__name=course_name).exclude(useful__exact="").count()
        useful = CourseRating.objects.filter(course__name=course_name, useful='yes').count()
        easy = CourseRating.objects.filter(course__name=course_name, easy='yes').count()
        liked = CourseRating.objects.filter(course__name=course_name, liked='yes').count()
    except:
        pass

    return JsonResponse({
        'total': total,
        'useful': useful,
        'easy': easy,
        'liked': liked,
    })


def get_attended_course_rating(request):
    course_name = request.GET.get('course_name').replace('_', ' ')
    teacher_first_name = request.GET.get('teacher_first_name')
    teacher_last_name = request.GET.get('teacher_last_name')
    try:
        total = AttendedCourse.objects.filter(
            course__name=course_name,
            teacher__first_name=teacher_first_name,
            teacher__last_name=teacher_last_name).exclude(clear__exact="").count()
        clear = AttendedCourse.objects.filter(
            course__name=course_name,
            teacher__first_name=teacher_first_name,
            teacher__last_name=teacher_last_name,
            clear='yes').count()
        engaging = AttendedCourse.objects.filter(
            course__name=course_name,
            teacher__first_name=teacher_first_name,
            teacher__last_name=teacher_last_name,
            engaging='yes').count()
        easy = AttendedCourse.objects.filter(
            course__name=course_name,
            teacher__first_name=teacher_first_name,
            teacher__last_name=teacher_last_name,
            easy='yes').count()
    except:
        pass

    return JsonResponse({
        'total': total,
        'clear': clear,
        'engaging': engaging,
        'easy': easy,
    })
