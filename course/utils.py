from django.contrib.auth.models import User

from accounts.models import Teacher, Student
from core.infra import GITLAB_
from .models import Course, Lab


def get_nav_side_dict(username, identity):
    """
    return 側邊欄所需要的 courses 和 labs 資料
    """
    courses = ''

    if identity == 'student':
        stu_id = Student.objects.filter(full_name=username).get().id
        courses = Course.objects.filter(students=stu_id)
    elif identity == 'teacher':
        tch_id = Teacher.objects.filter(full_name=username).get().id
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
