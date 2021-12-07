from django.shortcuts import render

from .forms import LabForm
from .models import Course
from accounts.models import Role, Teacher, Student
from accounts.utils.check_role import get_roles


def course_list_view(request):
    courses = {}

    if Role.STUDENT in get_roles(request.user):
        stu_id = Student.objects.filter(full_name=request.user.username).get().id
        courses = Course.objects.filter(students=stu_id)
    elif Role.TEACHER in get_roles(request.user):
        tch_id = Teacher.objects.filter(full_name=request.user.username).get().id
        courses = Course.objects.filter(teacher=tch_id)

    return render(request, 'course_list.html', {'courses': courses})


def course_view(request, course_id):

    return render(request, 'course_tch.html', {'course_id': course_id})
    # return render(request, 'course_stu.html', {'course_id': course_id})


def lab_view(request, course_id, lab_id):
    form = LabForm
    return render(request, 'lab_tch.html', {'form': form})
    # return render(request, 'lab_stu.html', {'form': form})


def lab_new_view(request, course_id):
    form = LabForm
    return render(request, 'lab_new.html', {'form': form})
