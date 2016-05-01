from django.contrib import admin

from .models import Course, Teacher, Student, AttendedCourse, CourseRating

admin.site.register(Course)
admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(AttendedCourse)
admin.site.register(CourseRating)
