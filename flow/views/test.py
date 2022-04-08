from django.shortcuts import render

from core.infra.gitlab_func import get_repo_verbose
from core.infra import SONAR_, SONARQUBE_URL
from core.infra.sonarqube_func import get_project_name


def reports_view(request, user, project):
    """顯示 測試報告"""
    project_info = get_repo_verbose(user, project)

    sonar_url = None
    sonar_info = None
    project_name = get_project_name(user, project)
    projects = list(SONAR_.projects.search_projects())
    # 檢查有無 sonarqube project
    for pro in projects:
        if project_name == pro['key']:
            sonar_url = f'{SONARQUBE_URL}/dashboard?id={project_name}'
            # 獲得 sonarqube 部分資訊 (metrics)
            metrics = 'bugs, vulnerabilities, security_hotspots, code_smells'
            sonar_measures = SONAR_.measures.get_component_with_specified_measures(component=project_name,
                                                                               metricKeys=metrics)
            sonar_info = {}
            measures = sonar_measures['component']['measures']
            for measure in measures:
                sonar_info[measure['metric']] = measure['value']
            break

    context = {
        'info': project_info,
        'have_sonarqube': True,
        'sonar_url': sonar_url,
        'sonar_info': sonar_info,
    }
    return render(request, 'test/reports.html', context)
