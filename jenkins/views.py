from django.shortcuts import render

from repo.utils import get_repo_title


def jenkins_file_view(request, user, project):
    """顯示 Jenkins File"""
    project_info = get_repo_title(user, project)

    if request.method == 'POST':
        print(request.POST.getlist('stage'))
        print(request.POST.getlist('single_sh'))
        print(request.POST.getlist('multi_sh'))
        print(request.POST.getlist('echo'))
        print(request.POST.get('context', ''))

    return render(request, 'jenkins/jenkins_file.html', {'info': project_info})
