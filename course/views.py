import csv
import os
from pathlib import PurePosixPath

from gitlab.exceptions import GitlabGetError

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse, Http404, HttpResponse

from accounts.models import Role, Teacher, Student
from accounts.utils.check_role import get_roles, check_role
from core.dicts import MESSAGE_DICT
from core.infra import GITLAB_, SONAR_
from core.infra.gitlab_func import get_repo_verbose, get_tree
from core.infra.sonarqube_func import get_project_name
from .forms import LabForm
from .models import Course, Lab, Question, Option, Answer
from .utils import get_nav_side_dict, create_user, create_stu_identity, \
    check_stu_lab_status, check_stu_evaluation_status, \
    count_stu_lab_submit, count_stu_evaluation_submit, question_parser
from flow.models import Project
from flow.forms import TemplateRepoForm
from flow.utils import import_template, create_jenkins_job, create_gitlab_webhook, same_name_repo
from flowlab.settings import MEDIA_ROOT


def course_list_view(request):
    """課程總覽"""
    context = {}

    if Role.STUDENT in get_roles(request.user):
        stu_id = Student.objects.filter(user=request.user).get().id
        context.update({'courses': Course.objects.filter(students=stu_id).order_by('id')})
        context.update(get_nav_side_dict(request.user, 'student'))
    elif Role.TEACHER in get_roles(request.user):
        tch_id = Teacher.objects.filter(user=request.user).get().id
        context.update({'courses': Course.objects.filter(teacher=tch_id).order_by('id')})
        context.update(get_nav_side_dict(request.user, 'teacher'))

    return render(request, 'course_list.html', context)


def course_view(request, course_id):
    """課程內容"""
    context = {
        'course_id': course_id,
        'labs': Lab.objects.filter(course=course_id).order_by('id'),
        'course': Course.objects.filter(id=course_id).get(),
        'project': {},
        'lab_submit': {},
        'eva_submit': {},
        'finish': {},
    }
    context.update({'students': context['course'].students.all()})

    if Role.STUDENT in get_roles(request.user):
        for lab in context['labs']:
            student_obj = context['course'].students.filter(user=request.user)
            submit_br = lab.branch
            # 檢查學生 lab 繳交狀態
            student_dict = check_stu_lab_status(lab)
            student = student_dict[request.user.username]
            if student['is_submit']:
                context['lab_submit'].update({
                    lab.name: '✔',
                })
            else:
                context['lab_submit'].update({
                    lab.name: '✖',
                })

            # 檢查學生 評量 填寫狀態
            students_eva = check_stu_evaluation_status(lab)
            student = students_eva[request.user.username]
            if student['is_finish']:
                context['eva_submit'].update({
                    lab.name: '✔',
                })
            else:
                context['eva_submit'].update({
                    lab.name: '✖',
                })

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

        context.update(get_nav_side_dict(request.user, 'student'))
        return render(request, 'course_stu.html', context)

    elif Role.TEACHER in get_roles(request.user):
        # 新增單筆學生資料
        if request.method == 'POST' and request.POST['action'] == 'create':
            username = request.POST['username']
            password = request.POST['password']
            name = request.POST['name']
            email = request.POST['email']

            # 建立使用者帳號
            user = create_user(request=request, username=username, password=password, name=name, email=email)
            # 建立學生身份, 並加入課程
            create_success = create_stu_identity(user=user, name=name, course_id=course_id)
            if create_success:
                messages.success(request, MESSAGE_DICT.get('create_stu_in_course_success').format(name))
            else:
                messages.warning(request, MESSAGE_DICT.get('stu_is_in_course').format(name))

        # 批量匯入學生資料
        elif request.method == 'POST' and request.POST['action'] == 'import':
            file_obj = request.FILES.get('file')
            file_path = os.path.join(MEDIA_ROOT, file_obj.name)
            # 將上傳的檔案 存到指定路徑下
            with open(file_path, 'wb') as file:
                for chunk in file_obj.chunks():
                    file.write(chunk)

            with open(file_path, 'r') as file:
                rows = csv.reader(file)
                for row in rows:
                    username = row[0]
                    password = row[1]
                    name = row[2]
                    email = row[3]

                    # 建立使用者帳號
                    user = create_user(request=request, username=username, password=password, name=name, email=email)
                    # 建立學生身份, 並加入課程
                    create_success = create_stu_identity(user=user, name=name, course_id=course_id)

                    if not create_success:
                        messages.warning(request, MESSAGE_DICT.get('stu_is_in_course').format(name))
                messages.success(request, MESSAGE_DICT.get('import_stu_in_course_success'))

            return HttpResponse('OK')

        # 將學生從課程中移除 (不會刪除 gitlab 帳號)
        elif request.method == 'POST' and request.POST['action'] == 'remove':
            # 將學生從課程中移除
            user = User.objects.get(username=request.POST['username'])
            student = Student.objects.get(user=user)
            course = Course.objects.get(id=course_id)
            course.students.remove(student)
            course.save()
            messages.success(request, MESSAGE_DICT.get('remove_stu_in_course_success').format(request.POST['name']))

        for lab in context['labs']:
            students_obj = context['course'].students.all()
            submit_br = lab.branch

            # 計算各 lab 學生繳交人數
            counts = count_stu_lab_submit(lab)
            context['lab_submit'][lab.name] = counts

            # 計算各 評量 學生繳交人數
            counts_eva = count_stu_evaluation_submit(lab)
            context['eva_submit'][lab.name] = counts_eva

        context.update(get_nav_side_dict(request.user, 'teacher'))
        return render(request, 'course_tch.html', context)


def lab_view(request, course_id, lab_id):
    """實驗內容"""
    lab = Lab.objects.filter(id=lab_id).get()
    form = LabForm(instance=lab)

    if Role.STUDENT in get_roles(request.user):
        repo_form = TemplateRepoForm(request.POST or None)

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
            'form': repo_form,
        }
        context.update(get_nav_side_dict(request.user, 'student'))

        # 按下更新按鈕, 更新關聯專案
        if request.method == 'POST' and request.POST['action'] == 'UpdateRepo':
            origin_repo = request.POST['origin_repo']
            selected_repo = request.POST['select_repo']

            # lab 有關聯到專案, 需要先刪除關聯的專案, 再建立新的關聯專案
            if origin_repo:
                repo_obj = Project.objects.get(user=request.user, name=origin_repo)
                # 刪除關聯的專案
                lab.project.remove(repo_obj)

            if selected_repo == '無':
                messages.success(request, MESSAGE_DICT.get('update_related_project'))
                return redirect('lab', course_id=course_id, lab_id=lab_id)

            # 建立關聯專案
            new_repo_obj = Project.objects.get(user=request.user, name=selected_repo)
            lab.project.add(new_repo_obj)

            context.update({'project': new_repo_obj})
            messages.success(request, MESSAGE_DICT.get('update_related_project'))

        # 使用模板建立新專案 (同時會關聯該專案)
        elif request.method == 'POST' and request.POST['action'] == 'CreateRepo':
            # 擷取常用變數
            username = request.user.username
            repo_name = request.POST['name']
            # 模板檔案
            template_file = lab.template.template

            # 檢查專案是否同名
            if same_name_repo(request, repo_name):
                return redirect('repo_list', user=username)

            # 將模板匯入專案
            project = import_template(
                username=username,
                repo_name=repo_name,
                template_file=template_file,
                description=request.POST['description'],
                visibility=request.POST['visibility'],
            )

            # 建立 Jenkins Job (Multibranch Pipeline 模板)
            create_jenkins_job(username=username, repo_name=repo_name)
            # 建立 GitLab webhook
            create_gitlab_webhook(username=username, repo_name=repo_name, project=project)
            # 建立 SonarQube project
            project_name = get_project_name(username, repo_name)
            SONAR_.projects.create_project(project=project_name, name=project_name)

            # 建立 Project model
            Project.objects.create(**{
                'user': request.user,
                'name': repo_name,
            })

            # 建立 Lab 與 Project 的關聯
            origin_repo = lab.project.filter(user=request.user)
            if origin_repo:
                # 若已有關聯, 需先刪除關聯的專案
                repo_obj = Project.objects.get(user=request.user, name=origin_repo)
                lab.project.remove(repo_obj)
            # 建立新關聯
            repo_obj = Project.objects.get(user=request.user, name=repo_name)
            lab.project.add(repo_obj)

            messages.success(request, MESSAGE_DICT.get('create_template_related_project').format(repo_name))

            return redirect('lab', course_id=course_id, lab_id=lab_id)

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
        context.update(get_nav_side_dict(request.user, 'teacher'))
        return render(request, 'lab_tch.html', context)


@check_role([Role.TEACHER])
def lab_new_view(request, course_id):
    """新增實驗 (lab)"""
    form = LabForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        course = Course.objects.get(id=course_id)
        form.instance.course = course
        # 新增 lab
        form.save()
        messages.success(request, MESSAGE_DICT.get('create_lab_success'))

        return redirect('course', course_id=course_id)

    return render(request, 'lab_new.html', {'form': form})


@check_role([Role.TEACHER])
def lab_submit_view(request, course_id, lab_id):
    """學生繳交 lab 與 互動式評量 的總覽頁面"""
    course = Course.objects.filter(id=course_id).get()
    students_obj = course.students.all()
    lab = Lab.objects.filter(id=lab_id).get()
    submit_br = lab.branch

    # 檢查學生 lab 繳交狀態
    students = check_stu_lab_status(lab)
    # 檢查學生 評量 填寫狀態
    students_eva = check_stu_evaluation_status(lab)

    context = {
        'course_id': course_id,
        'lab_id': lab_id,
        'course': course,
        'lab': lab,
        'students': students,
        'students_eva': students_eva,
    }

    return render(request, 'lab_submit_tch.html', context)


@check_role([Role.TEACHER])
def stu_tree_view(request, course_id, lab_id, student, project, path=''):
    """檢視學生的儲存庫資料夾"""
    lab = Lab.objects.filter(id=lab_id).get()
    branch = lab.branch

    project_info = get_repo_verbose(student, project)
    folders, files = get_tree(student, project, path, branch)

    context = {
        'course_id': course_id,
        'lab_id': lab_id,
        'student': student,
        'info': project_info,
        'tree_path': f'{path}/' if path else '',
        'folders': folders,
        'files': files,
    }
    return render(request, 'stu_repo/repo_tree.html', context)


@check_role([Role.TEACHER])
def stu_blob_view(request, course_id, lab_id, student, project, path):
    """檢視學生的儲存庫檔案"""
    lab = Lab.objects.filter(id=lab_id).get()
    branch = lab.branch

    full_path = PurePosixPath(path)
    blob = {
        'path': str(full_path.parent),
    }

    project_inst = GITLAB_.projects.get(f'{student}/{project}')
    project_info = get_repo_verbose(student, project)

    try:
        file = project_inst.files.get(file_path=str(full_path), ref=branch)
    except GitlabGetError:
        raise Http404(f'"{student}/{project}/{branch}/{path}" does not exist!')
    else:
        # 先解 base64, 然後要再進行一次 utf-8 decode
        content = file.decode().decode('utf-8')
        content = content.split('\n')

    blob.update({
        'name': full_path.name,
        'content': content,
        'format': full_path.name.rsplit('.')[-1]
    })

    return render(request, 'stu_repo/repo_blob.html', {
        'info': project_info,
        'student': student,
        'branch': branch,
        'blob': blob,
    })


def lab_evaluation_view(request, course_id, lab_id):
    """互動式評量"""
    context = {}
    course = Course.objects.filter(id=course_id).get()
    lab = Lab.objects.filter(id=lab_id).get()
    questions = Question.objects.filter(lab=lab).order_by('id')

    # 過濾出選擇題中對應的選項
    q_options = {}
    for question in questions:
        if question.type == 'single':
            option = Option.objects.filter(topic=question)
            q_options[question.id] = option

    if Role.STUDENT in get_roles(request.user):
        student = Student.objects.get(user=request.user)
        context.update(get_nav_side_dict(request.user, 'student'))
        # 過濾出問題對應的回答
        q_ans = {}
        for question in questions:
            ans = Answer.objects.filter(topic=question, student=student)
            if ans:
                q_ans[question.id] = ans.get()
            else:
                q_ans[question.id] = ''
        context.update({'q_ans': q_ans})

        if request.method == 'POST':
            question_ids = request.POST.getlist('id')
            # 更新每個問題的回答
            for id in question_ids:
                q_id = Question.objects.get(id=id)
                answer = Answer.objects.filter(student=student, topic=q_id)
                ans_content = request.POST.get(f'answer_{id}')
                if answer:
                    answer.update(content=ans_content)
                else:
                    Answer.objects.update_or_create(student=student, topic=q_id, content=ans_content)
            messages.success(request, MESSAGE_DICT.get('save_evaluation_success'))
            return redirect('lab', course_id=course_id, lab_id=lab_id)

    elif Role.TEACHER in get_roles(request.user):
        context.update(get_nav_side_dict(request.user, 'teacher'))
        # 新增問題
        if request.method == 'POST' and request.POST['action'] == 'newQuestion':
            q_exist = Question.objects.filter(lab=lab)
            number = q_exist.last().number if q_exist else 0
            Question.objects.update_or_create(type='text', content=request.POST['content'], lab=lab, number=number + 1)
            question_obj = Question.objects.get(type='text', content=request.POST['content'], lab=lab, number=number + 1)
            question_parser(question_obj, request.POST['content'])
            return redirect('lab_evaluation', course_id=course_id, lab_id=lab_id)
        # 更新問題
        elif request.method == 'POST' and request.POST['action'] == 'updateQuestion':
            question_obj = Question.objects.get(id=request.POST['id'])
            question_parser(question_obj, request.POST['content'])
            return redirect('lab_evaluation', course_id=course_id, lab_id=lab_id)
        # 刪除問題
        elif request.method == 'POST' and request.POST['action'] == 'delQuestion':
            Question.objects.get(id=request.POST['id']).delete()
            return redirect('lab_evaluation', course_id=course_id, lab_id=lab_id)

    context.update({
        'course': course,
        'lab': lab,
        'questions': questions,
        'q_options': q_options,
    })

    if Role.STUDENT in get_roles(request.user):
        return render(request, 'evaluation_stu.html', context)
    elif Role.TEACHER in get_roles(request.user):
        return render(request, 'evaluation_tch.html', context)


@check_role([Role.TEACHER])
def lab_evaluation_submit_view(request, course_id, lab_id, student):
    """老師檢視單個學生的互動式評量"""
    course = Course.objects.filter(id=course_id).get()
    lab = Lab.objects.filter(id=lab_id).get()
    questions = Question.objects.filter(lab=lab).order_by('id')
    # 獲取學生物件
    stu_id = User.objects.get(username=student)
    student_obj = Student.objects.get(user=stu_id)

    # 過濾出選擇題中對應的選項
    q_options = {}
    for question in questions:
        if question.type == 'single':
            option = Option.objects.filter(topic=question)
            q_options[question.id] = option

    # 過濾出問題對應的回答
    q_ans = {}
    for question in questions:
        pass
        ans = Answer.objects.filter(topic=question, student=student_obj)
        if ans:
            q_ans[question.id] = ans.get()

    context = {
        'course': course,
        'lab': lab,
        'student': student_obj,
        'questions': questions,
        'q_options': q_options,
        'q_ans': q_ans,
    }

    return render(request, 'evaluation_submit_tch.html', context)


@check_role([Role.TEACHER])
def lab_evaluation_total_view(request, course_id, lab_id):
    """老師檢視所有學生的互動式評量(統計結果)"""
    course = Course.objects.filter(id=course_id).get()
    lab = Lab.objects.filter(id=lab_id).get()
    questions = Question.objects.filter(lab=lab).order_by('id')
    # 計算 班級人數
    stu_total = course.students.count()
    students_obj = course.students.all()
    # 計算 已填寫評量人數
    stu_ans = count_stu_evaluation_submit(lab)

    # 過濾出選擇題中對應的選項
    q_options = {}
    for question in questions:
        if question.type == 'single':
            option = Option.objects.filter(topic=question)
            q_options[question.id] = option

    # 過濾出問題對應的回答
    q_ans = {}
    for question in questions:
        q_ans[question.id] = {}
        ans = Answer.objects.filter(topic=question)
        for op in q_options[question.id]:
            q_ans[question.id][op.number] = 0
        if ans:
            for a in ans:
                for op in q_options[question.id]:
                    if a.content == str(op.number):
                        q_ans[question.id][op.number] += 1
                        continue

    context = {
        'course': course,
        'lab': lab,
        'stu_noans': stu_total - stu_ans,
        'stu_ans': stu_ans,
        'questions': questions,
        'q_options': q_options,
        'q_ans': q_ans,
    }

    return render(request, 'evaluation_total_tch.html', context)
