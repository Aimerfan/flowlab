from django.shortcuts import render


def index(request):
    context = {
        'user': request.user,
        'username': '',
    }

    if request.user.is_authenticated:
        context['username'] = request.user.username

    return render(request, 'core/index.html', context)


def development(request):
    context = {}
    return render(request, 'development/development.html', context)
