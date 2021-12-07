from django.urls import path

from .views import course_list_view, course_view, lab_new_view, lab_view

urlpatterns = [
    path('', course_list_view, name='courses'),
    path('<int:course_id>/lab', course_view, name='labs'),
    path('<int:course_id>/lab/new', lab_new_view, name='lab_new'),
    path('<int:course_id>/lab/<int:lab_id>', lab_view, name='lab_detail')
]
