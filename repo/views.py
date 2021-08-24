from django.shortcuts import render


def repo_list_view(request, user):
    """儲存庫專案列表"""
    print(request.user)
    print(user)
    return render(request, 'repo/repo_list.html')


def repo_view(request, user, project):
    """儲存庫專案"""
    print(request.user)
    print(user, project)
    return render(request, 'repo/repository.html')
