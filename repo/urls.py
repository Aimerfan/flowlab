from django.urls import path

from .views import repo_view, repo_new_view, repo_list_view, repo_blob_view, repo_tree_view

urlpatterns = [
    path('', repo_view, name='repo'),
    path('<str:user>/', repo_list_view, name='repo_list'),
    path('new', repo_new_view, name='repo_new'),
    path('<str:user>/<str:project>/', repo_view, name='repo_project'),
    path('<str:user>/<str:project>/-/tree/<path:file>/', repo_tree_view, name='repo_tree'),
    path('<str:user>/<str:project>/-/blob/<path:file>/', repo_blob_view, name='repo_blob'),
]