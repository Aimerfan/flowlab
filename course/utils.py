from .models import Course, Lab
from accounts.models import Teacher, Student


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
