from django.urls import path

from .views import repo_view, repo_list_view

urlpatterns = [
    path('', repo_view, name='repo'),
    path('<str:user>/', repo_list_view, name='repo_list'),
    path('<str:user>/<str:project>/', repo_view, name='repo_project'),
]
