from django.shortcuts import render


def index(request):
    context = {
        'user': request.user,
        'username': '',
    }

    if request.user.is_authenticated:
        context['username'] = request.user.username

    return render(request, 'core/index.html', context)


def courses(request):
    context = {}
    return render(request, 'development/courses.html', context)


def repository(request):
    context = {}
    return render(request, 'development/repository.html', context)


def analysis(request):
    context = {}
    return render(request, 'development/analysis.html', context)
