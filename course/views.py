from django.shortcuts import render


def course_view(request):
    context = {}
    return render(request, 'course.html', context)


def lab_view(request, course_id):
    context = {}
    return render(request, 'lab.html', context)
