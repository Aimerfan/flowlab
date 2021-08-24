from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('courses/', views.courses, name='courses'),
    path('repository/', views.repository, name='repository'),
    path('analysis/', views.analysis, name='analysis'),
]
