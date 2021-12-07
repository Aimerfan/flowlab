from django.urls import path

from .views import course_view, lab_view

urlpatterns = [
    path('', course_view, name='courses'),
    path('<int:course_id>/lab', lab_view, name='labs'),
]
