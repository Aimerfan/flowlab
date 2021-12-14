from django.urls import path

from views import repo, ci, ajax

urlpatterns = [
    path('pipeparser/', ajax.create_jenkinsfile, name='pipeparser'),
    # FIXME: if username is 'new' with a repo name 'blank'
    path('new/blank', repo_new_blank, name='repo_new_blank'),
    path('new/template', repo_new_template, name='repo_new_template'),
    path('<str:user>/', repo_list_view, name='repo_list'),
    path('<str:user>/<str:project>/', repo_view, name='repo_project'),
    path('<str:user>/<str:project>/-/tree/<str:branch>/', repo_tree_view, name='repo_tree_root'),
    path('<str:user>/<str:project>/-/tree/<str:branch>/<path:path>/', repo_tree_view, name='repo_tree'),
    path('<str:user>/<str:project>/-/blob/<str:branch>/<path:path>/', repo_blob_view, name='repo_blob'),
    path('<str:user>/<str:project>/jenkisfile/', ci.jenkins_file_view, name='jenkins_file'),
    path('<str:user>/<str:project>/job/<str:branch>', ci.build_view, name='build'),
    path('<str:user>/<str:project>/job/<str:branch>/<int:number>', ci.build_console_view, name='build_console'),
]
