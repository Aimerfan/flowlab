from django.contrib.auth.models import User

from accounts.models import Teacher, Student
from core.infra import GITLAB_
from .models import Course, Lab, Question, Option, Answer


def get_nav_side_dict(user, identity):
    """
    return 側邊欄所需要的 courses 和 labs 資料
    """
    courses = ''

    if identity == 'student':
        stu_id = Student.objects.filter(user=user).get().id
        courses = Course.objects.filter(students=stu_id)
    elif identity == 'teacher':
        tch_id = Teacher.objects.filter(user=user).get().id
        courses = Course.objects.filter(teacher=tch_id)

    return {
        'courses': courses,
        'all_labs': Lab.objects.all(),
    }


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
        print(question_exist)
        if question_exist:
            # questions = question_exist.get()
            # print(questions)
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
