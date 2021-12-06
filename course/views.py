from django.shortcuts import render


def course_view(request):
    context = {}
    return render(request, 'course.html', context)
