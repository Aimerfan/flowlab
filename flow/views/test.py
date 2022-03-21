from django.shortcuts import render

from core.infra.gitlab_func import get_repo_verbose


def reports_view(request, user, project):
    """顯示 測試報告"""
    project_info = get_repo_verbose(user, project)
    context = {
        'info': project_info,
    }
    return render(request, 'test/reports.html', context)
