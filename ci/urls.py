from django.urls import path

from .views import jenkins_file_view, build_view, build_console_view, post_jenkinsfile_api

urlpatterns = [
    path('<str:user>/<str:project>/jenkisfile/', jenkins_file_view, name='jenkins_file'),
    path('<str:user>/<str:project>/job/<str:branch>', build_view, name='build'),
    path('<str:user>/<str:project>/job/<str:branch>/<int:number>', build_console_view, name='build_console'),
    path('pipeparser/', post_jenkinsfile_api, name='pipeparser'),
]
