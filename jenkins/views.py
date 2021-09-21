from django.shortcuts import render

from repo.utils import get_repo_title


def jenkins_file_view(request, user, project):
    """顯示 Jenkins File"""
    project_info = get_repo_title(user, project)

    return render(request, 'jenkins/jenkins_file.html', {'info': project_info})
