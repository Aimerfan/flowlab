from django.shortcuts import render

from core.infra.gitlab_func import get_repo_verbose
from core.infra import JENKINS_
from core.infra.jenkins_func import get_job_name, get_junit_result, get_coverage_result
from core.infra import SONAR_, SONARQUBE_URL
from core.infra.sonarqube_func import get_project_name


def reports_view(request, user, project, branch):
    """顯示 測試報告"""
    project_info = get_repo_verbose(user, project)

    # 檢查該分支的最新建構結果
    job_name = get_job_name(user, project, branch)
    junit_info = None
    coverage_info = None
    if JENKINS_.job_exists(job_name):
        multibr_default_job = JENKINS_.get_job_info(job_name)
        # 取得該 branch 最新的建置編號 (先確認是否有建置結果)
        if 'lastCompletedBuild' in multibr_default_job.keys():
            last_build_number = multibr_default_job['lastCompletedBuild']['number']
            # 檢查有無 junit 測試
            junit_info = get_junit_result(user=user, project=project, branch=branch, build_no=last_build_number)
            # 檢查有無 coverage 測試
            coverage_info = get_coverage_result(user=user, project=project, branch=branch, build_no=last_build_number)

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
        'branch': branch,
        'junit_info': junit_info,
        'coverage_info': coverage_info,
        'sonar_url': sonar_url,
        'sonar_info': sonar_info,
    }
    return render(request, 'test/reports.html', context)
