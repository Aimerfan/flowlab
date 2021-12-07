from django.shortcuts import render

from .forms import LabForm


def course_list_view(request):
    context = {}
    return render(request, 'course_list.html', context)


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
