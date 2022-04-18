from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

from .forms import LoginForm


def login_view(request):
    """登入"""
    next_url = request.GET.get('next', 'index')
    form = LoginForm(request.POST or None)

    # 已登入，重定向到首頁
    if request.user.is_authenticated:
        redirect(next_url)
    # 先驗證 http method
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user and user.is_active:
            login(request, user)
            return redirect(next_url)
        else:
            pass
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """登出"""
    logout(request)
    return redirect('index')
