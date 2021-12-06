from django.urls import path

from .views import course_view

urlpatterns = [
    path('', course_view, name='courses'),
]
