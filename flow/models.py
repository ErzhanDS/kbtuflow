from __future__ import unicode_literals

from django.db import models
from django.utils import timezone


class Teacher(models.Model):
    courses = models.ManyToManyField('Course', blank=True)

    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    image = models.TextField(default='http://s32.postimg.org/nnv9eh6tx/teacher.png')

    def __unicode__(self):
        return self.last_name + ' ' + self.first_name

    class Meta:
        ordering = ('last_name', 'first_name',)


class Course(models.Model):
    teachers = models.ManyToManyField(Teacher, through=Teacher.courses.through, blank=True)
    image = models.TextField(default='http://s32.postimg.org/o1wle2qxh/course.png')

    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class Student(models.Model):
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    registered_date = models.DateTimeField(default=timezone.now)

    def __unicode__(self):
        return self.username + ': ' + self.last_name + ' ' + self.first_name

    class Meta:
        ordering = ('username',)


class AttendedCourse(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    clear = models.CharField(max_length=200)
    engaging = models.CharField(max_length=200)
    easy = models.CharField(max_length=200)

    def __unicode__(self):
        return self.course.name + ' by ' + self.teacher.last_name + ' ' + self.teacher.first_name + ', taken by ' + self.student.last_name + ' ' + self.student.first_name


class CourseRating(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    useful = models.CharField(max_length=200)
    easy = models.CharField(max_length=200)
    liked = models.CharField(max_length=200)

    def __unicode__(self):
        return self.course.name + ' rated by ' + self.student.last_name + ' ' + self.student.first_name
