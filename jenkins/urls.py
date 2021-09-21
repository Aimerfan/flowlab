from django.urls import path

from .views import jenkins_file_view

urlpatterns = [
    path('<str:user>/<str:project>/jenkisfile/', jenkins_file_view, name='jenkins_file'),
]
