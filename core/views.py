from django.shortcuts import render


def index(request):
    context = {}
    return render(request, 'index.html', context)


def courses(request):
    context = {}
    return render(request, 'dev/courses.html', context)


def analysis(request):
    context = {}
    return render(request, 'dev/analysis.html', context)
