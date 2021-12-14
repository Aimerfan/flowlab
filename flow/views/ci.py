from django.shortcuts import render
from django.contrib import messages

from core.infra import JENKINS_
from core.infra.jenkins_func import get_job_name
from core.infra.gitlab_func import get_repo_verbose
from core.dicts import MESSAGE_DICT
from ..forms import TestSelectForm
from ..utils import update_jenkinsfile, push_jenkinsfile


def jenkins_file_view(request, user, project):
    """顯示 Jenkins File"""
    form = TestSelectForm(request.POST or None)
    project_info = get_repo_verbose(user, project)
    repo_name = f'{user}/{project}'
    pipe_content = ''
    selected_branch = ''

    if request.method == 'POST':
        # 修改並顯示 Jenkinsfile
        if request.POST['action'] == 'update' and form.is_valid():
            # 讀取選擇的分支與測試
            selected_branch = request.POST.get('selected_branch')
            selected_tests = form.cleaned_data['selected_tests']
            pipe_content = update_jenkinsfile(repo_name, selected_branch, selected_tests)
        # 將前端顯示的 Jenkisfile 推至儲存庫
        elif request.POST['action'] == 'push':
            selected_branch = request.POST.get('selected_branch')
            pipe_content = request.POST.get('pipe_content')
            push_jenkinsfile(repo_name, selected_branch, pipe_content)
            messages.success(request, MESSAGE_DICT.get('push_jenkinsfile_success'))

    return render(request, 'ci/jenkins_file.html', {
        'info': project_info,
        'test_select_form': form,
        'pipe_content': pipe_content,
        'selected_branch': selected_branch,
    })


def build_view(request, user, project, branch):
    project_info = get_repo_verbose(user, project)
    job_name = get_job_name(user, project, branch)

    build_results = {}

    if JENKINS_.job_exists(job_name):
        multibr_default_job = JENKINS_.get_job_info(job_name)
        # 取得該 branch 最新的建置編號
        last_build_number = multibr_default_job['lastCompletedBuild']['number']
        # 取得該 branch 的最新 5 個建置結果 (由新至舊)
        for number in range(last_build_number, last_build_number - 5, -1):
            if number > 0:
                build_info = JENKINS_.get_build_console_output(job_name, number).split('\n')
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
    build_info = JENKINS_.get_build_console_output(job_name, number).split('\n')

    return render(request, 'ci/build_console.html', {'info': project_info, 'build_info': build_info})
