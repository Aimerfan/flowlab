from django.shortcuts import render

from .forms import LabForm
from .models import Course, Lab
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

    context = {
        'labs': Lab.objects.filter(course=course_id),
        'course_id': course_id,
        'course_name': Course.objects.filter(id=course_id).get().name,
    }

    if Role.STUDENT in get_roles(request.user):
        return render(request, 'course_stu.html', context)
    elif Role.TEACHER in get_roles(request.user):
        return render(request, 'course_tch.html', context)


def lab_view(request, course_id, lab_id):
    form = LabForm
    return render(request, 'lab_tch.html', {'form': form})
    # return render(request, 'lab_stu.html', {'form': form})


def lab_new_view(request, course_id):
    form = LabForm
    return render(request, 'lab_new.html', {'form': form})
