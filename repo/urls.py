from django.urls import path

from .views import repo_view,\
    repo_new_blank,\
    repo_new_template,\
    repo_list_view,\
    repo_blob_view,\
    repo_tree_view

urlpatterns = [
    path('<str:user>/', repo_list_view, name='repo_list'),
    path('<str:user>/<str:project>/', repo_view, name='repo_project'),
    path('new/blank', repo_new_blank, name='repo_new_blank'),
    path('new/template', repo_new_template, name='repo_new_template'),
    path('<str:user>/<str:project>/-/tree/<str:branch>/', repo_tree_view, name='repo_tree_root'),
    path('<str:user>/<str:project>/-/tree/<str:branch>/<path:path>/', repo_tree_view, name='repo_tree'),
    path('<str:user>/<str:project>/-/blob/<str:branch>/<path:path>/', repo_blob_view, name='repo_blob'),
]
