import json

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

from repo.utils import get_job_name, get_repo_verbose
from .jenkins import jenkins_inst
from .pipeparser import PipeParser
from .forms import TestSelectForm


def jenkins_file_view(request, user, project):
    """顯示 Jenkins File"""
    form = TestSelectForm(request.POST or None)

    if request.method == 'POST':
        selected_tests = request.POST.getlist('selected_tests')
        # print(selected_tests)
        # TODO: 處理選擇的測試

    project_info = get_repo_verbose(user, project)

    return render(request, 'ci/jenkins_file.html', {'info': project_info, 'test_select_form': form})


def build_view(request, user, project, branch):
    project_info = get_repo_verbose(user, project)
    job_name = get_job_name(user, project, branch)

    build_results = {}

    if jenkins_inst.job_exists(job_name):
        multibr_default_job = jenkins_inst.get_job_info(job_name)
        # 取得該 branch 最新的建置編號
        last_build_number = multibr_default_job['lastCompletedBuild']['number']
        # 取得該 branch 的最新 5 個建置結果 (由新至舊)
        for number in range(last_build_number, last_build_number - 5, -1):
            if number > 0:
                build_info = jenkins_inst.get_build_console_output(job_name, number).split('\n')
                last_line = build_info[-2]
                # 擷取 console 的結果
                if 'SUCCESS' in last_line:
                    build_results[number] = 'success'
                elif 'FAILURE' in last_line:
                    build_results[number] = 'failure'
                elif 'ABORTED' in last_line:
                    build_results[number] = 'stop'
                else:
                    build_results[number] = ''

    return render(request, 'ci/build.html', {
        'info': project_info,
        'branch': branch,
        'build_results': build_results,
    })


def build_console_view(request, user, project, branch, number):
    project_info = get_repo_verbose(user, project)
    job_name = get_job_name(user, project, branch)

    # 取得 console output
    build_info = jenkins_inst.get_build_console_output(job_name, number).split('\n')

    return render(request, 'ci/build_console.html', {'info': project_info, 'build_info': build_info})


@csrf_exempt
def post_jenkinsfile_api(request):
    # valid ajax request
    if not request.is_ajax() or request.method != 'POST':
        return HttpResponseBadRequest('error request type, must be ajax by POST method.')
    
    pipe_tree = PipeParser.parse(json.loads(request.body))
    return HttpResponse(pipe_tree.__str__(), headers={
        'Content-Type': 'text/plain',
    })
