from django.shortcuts import render


def course_view(request):
    context = {}
    return render(request, 'course.html', context)


def lab_view(request, course_id):
    context = {}
    return render(request, 'lab.html', context)


def lab_detail_view(request, course_id, lab_id):
    context = {}
    return render(request, 'lab_detail.html', context)
