from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('development/', views.development, name='development'),
    path('repository/', views.repository, name='repository'),
    path('analysis/', views.analysis, name='analysis'),
]
