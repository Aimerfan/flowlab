from django.shortcuts import render
from django.contrib import messages
from django.http import JsonResponse

from core.dicts import MESSAGE_DICT
from .forms import LabForm
from .models import Course, Lab
from .utils import get_nav_side_dict
from accounts.models import Role, Teacher, Student
from accounts.utils.check_role import get_roles


def course_list_view(request):
    context = {}

    if Role.STUDENT in get_roles(request.user):
        stu_id = Student.objects.filter(full_name=request.user.username).get().id
        context.update({'courses': Course.objects.filter(students=stu_id)})
        context.update(get_nav_side_dict(request.user.username, 'student'))
    elif Role.TEACHER in get_roles(request.user):
        tch_id = Teacher.objects.filter(full_name=request.user.username).get().id
        context.update({'courses': Course.objects.filter(teacher=tch_id)})
        context.update(get_nav_side_dict(request.user.username, 'teacher'))

    return render(request, 'course_list.html', context)


def course_view(request, course_id):

    context = {
        'labs': Lab.objects.filter(course=course_id),
        'course': Course.objects.filter(id=course_id).get(),
    }
    context.update({'students': context['course'].students.all()})

    if Role.STUDENT in get_roles(request.user):
        context.update(get_nav_side_dict(request.user.username, 'student'))
        return render(request, 'course_stu.html', context)

    elif Role.TEACHER in get_roles(request.user):
        context.update(get_nav_side_dict(request.user.username, 'teacher'))
        return render(request, 'course_tch.html', context)


def lab_view(request, course_id, lab_id):
    lab = Lab.objects.filter(id=lab_id).get()
    form = LabForm(instance=lab)

    if Role.STUDENT in get_roles(request.user):
        context = {
            'course_id': course_id,
            'lab': lab,
        }
        context.update(get_nav_side_dict(request.user.username, 'student'))
        return render(request, 'lab_stu.html', context)

    elif Role.TEACHER in get_roles(request.user):
        # 更新 lab 資訊
        if request.method == 'POST':
            form = LabForm(request.POST, instance=lab)
            form.save()
            # TODO: 若 "繳交期限" 未重新選擇, 會被更新成空值
            messages.success(request, MESSAGE_DICT.get('update_lab_success'))
        # 刪除 lab
        elif request.method == 'DELETE':
            lab.delete()
            messages.success(request, MESSAGE_DICT.get('delete_lab_success'))
            return JsonResponse({'status': 200})

        context = {
            'course_id': course_id,
            'lab_id': lab_id,
            'form': form,
        }
        context.update(get_nav_side_dict(request.user.username, 'teacher'))
        return render(request, 'lab_tch.html', context)


def lab_new_view(request, course_id):
    form = LabForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        course = Course.objects.get(id=course_id)
        form.instance.course = course
        # 新增 lab
        form.save()
        messages.success(request, MESSAGE_DICT.get('create_lab_success'))

        context = {
            'labs': Lab.objects.filter(course=course_id),
            'course': Course.objects.filter(id=course_id).get(),
        }
        return render(request, 'course_tch.html', context)

    return render(request, 'lab_new.html', {'form': form})
