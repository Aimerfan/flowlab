from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout


def login_view(request):
    """登入"""
    # 已登入，重定向到首頁
    if request.user.is_authenticated:
        redirect('')
    # 先驗證 http method
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user and user.is_active:
            login(request, user)
            return redirect('index')
        else:
            pass
    return render(request, 'accounts/login.html', {})


def logout_view(request):
    """登出"""
    logout(request)
    return redirect('index')
