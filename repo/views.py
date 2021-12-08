import logging
from time import sleep
from datetime import datetime
from pathlib import PurePosixPath
from pkgutil import get_data

from gitlab.exceptions import GitlabGetError

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_http_methods

from core.dicts import MESSAGE_DICT
from core.gitlab import GITLAB_, GITLAB_URL
from core.gitlab.functools import timedelta_str, get_repo_verbose, get_tree
from core.jenkins import JENKINS_, JENKINS_URL, CONFIG_XML
from core.jenkins.functools import get_job_name
from .forms import BlankRepoForm, TemplateRepoForm

logger = logging.getLogger(f'flowlab.{__name__}')


def repo_list_view(request, user):
    """檢視儲存庫列表"""
    try:
        gitlab_user = GITLAB_.users.list(username=user)[0]
    except IndexError:
        logger.error(f"gitlab user '{user}' does not exist")
        messages.error(request, MESSAGE_DICT.get('gitlab_user_not_found'))
        raise Http404
    else:
        project_list = gitlab_user.projects.list()

    projects = {}
    for project_meta in project_list:
        # 取得專案最後的活動時間
        last_updated = project_meta.last_activity_at.replace('Z', '+00:00')
        now_last_delta = timezone.now() - datetime.fromisoformat(last_updated)

        # 根據 project meta 資訊獲得更詳細的的 project obj, 以計算 branches 數
        try:
            project = GITLAB_.projects.get(f'{user}/{project_meta.name}')
        except GitlabGetError:
            logger.warning(f"gitlab project {user}/{project_meta.name} does not exist")
            messages.warning(request, MESSAGE_DICT.get('gitlab_project_not_found').format(project_meta.name))
        else:
            branch_list = project.branches.list()

            # 放進 projects 清單
            projects[project_meta.name] = {
                'last_activity_at': timedelta_str(now_last_delta.total_seconds()),
                'branch_sum': len(branch_list),
            }

    return render(request, 'repo/repo_list.html', {'projects': projects})


@require_http_methods(['GET', 'HEAD', 'DELETE'])
def repo_view(request, user, project):
    """檢視儲存庫內容"""

    if request.method == 'DELETE':
        full_project_name = f'{user}/{project}'
        # 刪除 gitlab project
        GITLAB_.projects.get(full_project_name).delete()

        # 刪除 Jenkins Job
        job_name = get_job_name(user, project)
        if JENKINS_.get_job_name(job_name):
            JENKINS_.delete_job(job_name)
        return JsonResponse({'status': 200})

    # 判斷如果是空儲存庫，給空的預設值
    project_info = get_repo_verbose(user, project)
    if project_info['branch_sum'] == 0:
        folders = files = root_path = ''
    else:
        folders, files = get_tree(user, project)
        root_path = f'{project}/'

    content = {
        'info': project_info,
        'root_path': root_path,
        'folders': folders,
        'files': files,
    }
    return render(request, 'repo/repository.html', content)


def repo_tree_view(request, user, project, branch, path=''):
    """檢視儲存庫資料夾"""
    project_info = get_repo_verbose(user, project)
    folders, files = get_tree(user, project, path, branch)

    content = {
        'info': project_info,
        'tree_path': f'{path}/' if path else '',
        'folders': folders,
        'files': files,
        'branch': branch,
    }
    return render(request, 'repo/repo_tree.html', content)


def repo_blob_view(request, user, project, branch, path):
    """檢視儲存庫檔案"""
    full_path = PurePosixPath(path)
    blob = {
        'path': str(full_path.parent),
    }

    project_inst = GITLAB_.projects.get(f'{user}/{project}')
    project_info = get_repo_verbose(user, project)

    try:
        file = project_inst.files.get(file_path=str(full_path), ref=branch)
    except GitlabGetError:
        raise Http404(f'"{user}/{project}/{branch}/{path}" does not exist!')
    else:
        # 先解 base64, 然後要再進行一次 utf-8 decode
        content = file.decode().decode('utf-8')

    # 計算 'Lines Of Code'
    loc = content.count('\n')
    if content != '' and content[-1] != '\n':
        loc += 1

    blob.update({
        'name': full_path.name,
        'loc': loc,
        'content': content,
    })

    return render(request, 'repo/repo_blob.html', {
        'info': project_info,
        'branch': branch,
        'blob': blob,
    })


def repo_new_blank(request):
    """新增儲存庫"""
    form = BlankRepoForm(request.POST or None)

    if request.method == 'POST':
        username = request.user.username
        repo_name = request.POST['name']
        
        # 建立 gitlab project
        repo_meta = {
            'name': repo_name,
            'description': request.POST['description'],
            'visibility': request.POST['visibility'],
        }
        gitlab_user = GITLAB_.users.list(username=username)[0]
        user_project = gitlab_user.projects.create(repo_meta)
        # TODO: add file when create repo
        add_file = request.POST.getlist('add_file')
        # TODO: error message tips
        if user_project is None:
            raise Exception('repo create error.')

        # 建立 Jenkins Job (Multibranch Pipeline 模板)
        job_name = get_job_name(username, repo_name)
        if JENKINS_.job_exists(job_name):
            raise Exception('job already exists.')
        gitlab_repo_url = f"{GITLAB_URL}/{username}/{repo_name}"
        config_xml = CONFIG_XML.replace('set_remote', gitlab_repo_url)
        JENKINS_.create_job(job_name, config_xml)

        # 建立 GitLab webhook
        jenkins_webhook_url = f'{JENKINS_URL}/project/{job_name}'
        gitlab_webhook = {
            'url': jenkins_webhook_url,
            'push_events': 1,
            'merge_requests_events': 1,
        }
        project = GITLAB_.projects.get(user_project.id)
        if project.hooks.list():
            raise Exception('webhook in github already exists.')
        project.hooks.create(gitlab_webhook)

        return redirect('repo_project', user=username, project=repo_name)

    return render(request, 'repo/repo_new_blank.html', {'form': form})


def repo_new_template(request):
    """新增模板儲存庫"""
    form = TemplateRepoForm(request.POST or None)

    if request.method == 'POST':
        # 先驗證表單資訊
        if not form.is_valid():
            return redirect('repo_new_template')

        # 擷取常用變數
        selected_template = form.cleaned_data['template']
        username = request.user.username
        repo_name = form.cleaned_data['name']

        # 從 local repo_templates 匯入專案模板
        template_path = f'resources/repo_templates/{selected_template}'
        template = get_data(__name__, template_path)
        # 匯入到 gitlab
        output = GITLAB_.projects.import_project(
            file=template,
            path=repo_name,
            namespace=username,
            overwrite=False,
        )
        project_import = GITLAB_.projects.get(output['id'], lazy=True).imports.get()
        # 等待直到匯入完成
        while project_import.import_status != 'finished':
            sleep(1)
            project_import.refresh()

        # 匯入後根據表單更新專案設定值
        created_project = GITLAB_.projects.get(f'{username}/{repo_name}')
        created_project.description = form.cleaned_data['description']
        created_project.visibility = form.cleaned_data['visibility']
        created_project.save()

        return redirect('repo_project', user=username, project=repo_name)

    return render(request, 'repo/repo_new_template.html', {'form': form})
