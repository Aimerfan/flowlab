from django.shortcuts import render
from django.contrib import messages
from django.http import JsonResponse

from core.dicts import MESSAGE_DICT
from core.infra import GITLAB_
from .forms import LabForm
from .models import Course, Lab
from .utils import get_nav_side_dict
from flow.models import Project
from accounts.models import Role, Teacher, Student
from accounts.utils.check_role import get_roles


def course_list_view(request):
    """課程總覽"""
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
    """課程內容"""
    context = {
        'labs': Lab.objects.filter(course=course_id),
        'course': Course.objects.filter(id=course_id).get(),
        'project': {},
    }
    context.update({'students': context['course'].students.all()})

    if Role.STUDENT in get_roles(request.user):
        for lab in context['labs']:
            # 找出與 lab 關聯的專案
            project = lab.project.filter(user=request.user)
            # 若找的到, lab 對應到'專案名稱'
            if project:
                project_dict = {
                    lab: project.get().name
                }
            # 若找不到, lab 對應到'空值', 前端會顯示'無'
            else:
                project_dict = {
                    lab: ''
                }
            context['project'].update(project_dict)

        context.update(get_nav_side_dict(request.user.username, 'student'))
        return render(request, 'course_stu.html', context)

    elif Role.TEACHER in get_roles(request.user):
        context.update(get_nav_side_dict(request.user.username, 'teacher'))
        return render(request, 'course_tch.html', context)


def lab_view(request, course_id, lab_id):
    """實驗內容"""
    lab = Lab.objects.filter(id=lab_id).get()
    form = LabForm(instance=lab)

    if Role.STUDENT in get_roles(request.user):
        # 找出與 lab 關聯的專案
        project = lab.project.filter(user=request.user)
        if project:
            project = project.get()

        # 列出有關 user 的所有 gitlab 專案
        gitlab_user = GITLAB_.users.list(username=request.user.username)[0]
        project_list = gitlab_user.projects.list()

        context = {
            'course_id': course_id,
            'lab': lab,
            'project': project,
            'project_list': project_list,
        }
        context.update(get_nav_side_dict(request.user.username, 'student'))

        # 按下更新按鈕, 更新關聯專案
        if request.method == 'POST':
            origin_repo = request.POST['origin_repo']
            selected_repo = request.POST['select_repo']

            # lab 有關聯到專案, 需要先刪除關聯的專案, 再建立新的關聯專案
            if origin_repo:
                repo_obj = Project.objects.get(user=request.user, name=origin_repo)
                # 刪除關聯的專案
                lab.project.remove(repo_obj)

            # 建立關聯專案
            new_repo_obj = Project.objects.get(user=request.user, name=selected_repo)
            lab.project.add(new_repo_obj)

            context.update({'project': new_repo_obj})
            messages.success(request, MESSAGE_DICT.get('update_related_project'))

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
    """新增實驗 (lab)"""
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
