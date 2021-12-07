from django.urls import path

from .views import course_view, lab_view, lab_new_view, lab_detail_view

urlpatterns = [
    path('', course_view, name='courses'),
    path('<int:course_id>/lab', lab_view, name='labs'),
    path('<int:course_id>/lab/new', lab_new_view, name='lab_new'),
    path('<int:course_id>/lab/<int:lab_id>', lab_detail_view, name='lab_detail')
]
