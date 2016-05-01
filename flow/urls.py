from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register-student/$', views.register_student),
    url(r'^update-attended-course/$', views.update_attended_course),
    url(r'^update-course-rating/$', views.update_course_rating),
    url(r'^get-course-rating/$', views.get_course_rating),
    url(r'^get-attended-course-rating/$', views.get_attended_course_rating),
]
