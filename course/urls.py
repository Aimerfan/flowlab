from django.urls import path

from .views import \
    course_list_view, \
    course_view, \
    lab_new_view, \
    lab_view, \
    lab_evaluation_view, \
    lab_submit_view, \
    stu_tree_view, \
    stu_blob_view

urlpatterns = [
    path('', course_list_view, name='courses'),
    path('<int:course_id>', course_view, name='course'),
    path('<int:course_id>/lab/new', lab_new_view, name='lab_new'),
    path('<int:course_id>/lab/<int:lab_id>', lab_view, name='lab'),
    path('<int:course_id>/lab/<int:lab_id>/evaluation', lab_evaluation_view, name='lab_evaluation'),
    path('<int:course_id>/lab/<int:lab_id>/submit', lab_submit_view, name='lab_submit'),
    path('<int:course_id>/lab/<int:lab_id>/submit/<str:student>/<str:project>/-/tree/', stu_tree_view,
         name='stu_tree_root'),
    path('<int:course_id>/lab/<int:lab_id>/submit/<str:student>/<str:project>/-/tree/<path:path>/', stu_tree_view,
         name='stu_tree'),
    path('<int:course_id>/lab/<int:lab_id>/submit/<str:student>/<str:project>/-/blob/<path:path>/', stu_blob_view,
         name='stu_blob'),
]
