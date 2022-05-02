import logging
import requests

from django.contrib import messages
from django.contrib.auth.models import User

from accounts.models import Teacher, Student
from core.dicts import MESSAGE_DICT
from core.infra import GITLAB_
from core.infra import JENKINS_URL, JENKINS_AUTH
from core.infra import SONAR_
from .models import Course, Lab, Question, Option, Answer

logger = logging.getLogger(f'flowlab.{__name__}')


def get_nav_side_dict(user, identity):
    """
    return 側邊欄所需要的 courses 和 labs 資料
    """
    courses = ''

    if identity == 'student':
        stu_id = Student.objects.filter(user=user).get().id
        courses = Course.objects.filter(students=stu_id).order_by('id')
    elif identity == 'teacher':
        tch_id = Teacher.objects.filter(user=user).get().id
        courses = Course.objects.filter(teacher=tch_id).order_by('id')

    return {
        'courses': courses,
        'all_labs': Lab.objects.all().order_by('id'),
    }


def create_user(request, username, password, name, email=''):
    """
    建立使用者帳號, 並建立學生身分
    包含 GitLab, Jenkins, SonarQube
    return User obj.
    """
    # 建立使用者帳號
    if User.objects.filter(username=username):
        user = User.objects.get(username=username)
    else:
        user = User.objects.create_user(username=username, password=password, email=email)
        user.save()

        # 建立 GitLab 帳號
        gl_user = GITLAB_.users.create({'username': username, 'password': password,
                                        'name': name, 'email': email, 'skip_confirmation': True})
        gl_user.save()
        # 建立 Jenkins 帳號
        create_jenkins_user(request=request, username=username, password=password, email=email)
        # 建立 SonarQube 帳號
        SONAR_.users.create_user(login=username, name=name, password=password, email=email)

    return user


def create_jenkins_user(request, username, password, email):
    """建立 Jenkins 帳號"""

    data = {
        'username': username,
        'password1': password,
        'password2': password,
        'fullname': username,
        'email': email,
    }

    api_url = f'{JENKINS_URL}/securityRealm/createAccountByAdmin'
    result = requests.post(api_url, data=data, auth=JENKINS_AUTH)

    if result.status_code != requests.codes.ok:
        logger.error(f"create '{username}' jenkins account failed")
        logger.error(result.text)
        messages.error(request, MESSAGE_DICT.get('create_jenkins_user_failed'))


def create_stu_identity(user, name, course_id):
    """建立學生身份, 並加入課程"""
    # 建立學生身分
    if Student.objects.filter(user=user):
        student = Student.objects.get(user=user)
    else:
        student = Student.objects.create(user=user, full_name=name)
        student.save()

    # 將學生加入課程
    course = Course.objects.get(id=course_id)
    if course.students.filter(user=user):
        return False
    else:
        course.students.add(student)
        course.save()
        return True


def check_stu_lab_status(lab, students_obj, submit_br):
    """
    檢查學生 lab 繳交狀態
    1. 是否指定專案 (stu_repo_name)
    2. 是否繳交指定分支 (is_submit)
    """
    students = {}
    for student in students_obj:
        stu_username = student.user.username
        stu_id = User.objects.get(username=stu_username)
        stu_name = Student.objects.get(user=stu_id).full_name
        stu_repo = lab.project.filter(user=stu_id)

        stu_repo_name = None
        is_submit = False

        if stu_repo:
            stu_repo_name = stu_repo.get().name
            project = GITLAB_.projects.get(f'{stu_username}/{stu_repo_name}')
            branches = project.branches.list()
            # 檢查學生是否建立 lab 指定的 branch 分支
            for branch in branches:
                if branch.name == submit_br:
                    is_submit = True
                    break

        students[stu_username] = {
            'stu_name': stu_name,
            'repo_name': stu_repo_name,
            'is_submit': is_submit,
        }
    return students


def check_stu_evaluation_status(lab, students_obj):
    """
    檢查學生 評量 填寫狀態
    """
    students = {}
    for student in students_obj:
        stu_username = student.user.username

        is_finish = False
        question_exist = Question.objects.filter(lab=lab)
        if question_exist:
            for question in question_exist:
                answer = Answer.objects.filter(student=student, topic=question)
                if answer:
                    is_finish = True
                    break

        students[stu_username] = {
            'full_name': student,
            'is_finish': is_finish,
        }
    return students


def count_stu_lab_submit(lab, students_obj, submit_br):
    """計算已繳交 實驗 的學生數量"""
    students_lab = check_stu_lab_status(lab, students_obj, submit_br)
    # 計算各 lab 學生繳交人數
    counts = 0
    for name in students_lab:
        if students_lab[name]['is_submit']:
            counts += 1
    return counts


def count_stu_evaluation_submit(lab, students_obj):
    """計算已繳交 評量 的學生數量"""
    students_eva = check_stu_evaluation_status(lab, students_obj)
    counts = 0
    for name in students_eva:
        if students_eva[name]['is_finish']:
            counts += 1
    return counts


def question_parser(question_obj, content):
    """
    剖析 'question' 字串, 區分成 題目 (Topic) 與 選項 (Option)
    題目: 開頭不為 '()'
    選項: 開頭須為 '()' or '() '
    """
    lines = content.split('\n')
    topic = ''
    number = 0
    if question_obj.type == 'single':
        Option.objects.filter(topic=question_obj).delete()

    for line in lines:
        # 該行為 '選項' 的情況
        if line[0] == '(' and line[1] == ')':
            number = number + 1
            option_text = line[2:] if line[2] != ' ' else line[3:]
            Option.objects.update_or_create(topic=question_obj, number=number, content=option_text)
        else:
            topic += line

    if number:
        question_obj.type = 'single'
    else:
        question_obj.type = 'text'

    question_obj.content = topic
    question_obj.save()
