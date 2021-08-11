from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    return HttpResponse("Hello, world. You're at the index.")


def development(request):
    context = {}
    return render(request, 'development/development.html', context)


def login(request):
    context = {}
    return render(request, 'development/login.html', context)
