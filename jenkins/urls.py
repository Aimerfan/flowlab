from django.urls import path

from .views import jenkins_file_view, post_jenkinsfile_api

urlpatterns = [
    path('<str:user>/<str:project>/jenkisfile/', jenkins_file_view, name='jenkins_file'),
    path('pipeparser/', post_jenkinsfile_api, name='pipeparser'),
]
