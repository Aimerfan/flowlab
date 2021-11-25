from datetime import datetime
from pathlib import PurePosixPath
from base64 import b64decode

from django.shortcuts import render, redirect
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from core.utils import CONFIG_XML
from ci.jenkins import jenkins_inst, jenkins_url
from .gitlab import gitlab_inst, gitlab_url
from .utils import get_job_name, timedelta_str, get_repo_verbose, get_tree
from .forms import RepoForm


def repo_list_view(request, user):
    """檢視儲存庫列表"""
    gitlab_user = gitlab_inst.users.list(username=user)[0]
    project_list = gitlab_user.projects.list()

    projects = {}
    for project_meta in project_list:
        # 取得專案最後的活動時間
        last_updated = project_meta.last_activity_at.replace('Z', '+00:00')
        now_last_delta = timezone.now() - datetime.fromisoformat(last_updated)

        # 根據 project meta 資訊獲得更詳細的的 project obj, 以計算 branches 數
        project = gitlab_inst.projects.get(f'{user}/{project_meta.name}')
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
        gitlab_inst.projects.get(full_project_name).delete()

        # 刪除 Jenkins Job
        job_name = get_job_name(user, project)
        if jenkins_inst.get_job_name(job_name):
            jenkins_inst.delete_job(job_name)
        return JsonResponse({'status': 200})

    # 通過 utils 取得 project(repo) 詳細訊息
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

    project_inst = gitlab_inst.projects.get(f'{user}/{project}')
    project_info = get_repo_verbose(user, project)

    trees = project_inst.repository_tree(path=blob['path'], ref=branch)
    # 列出 path_tree 下的 subtree, 搜尋 request 的 blob
    for tree in trees:
        if tree['name'] == full_path.name and tree['type'] == 'blob':
            gl_blob = project_inst.repository_blob(tree['id'])
            content = b64decode(gl_blob['content']).decode('utf-8')

            # account 'Lines Of Code'
            loc = content.count('\n')
            if content != '' and content[-1] != '\n':
                loc += 1

            blob.update({
                'name': full_path.name,
                'loc': loc,
                'content': content,
            })
            break

    return render(request, 'repo/repo_blob.html', {
        'info': project_info,
        'branch': branch,
        'blob': blob,
    })


def repo_new_view(request):
    """新增儲存庫"""
    form = RepoForm(request.POST or None)

    if request.method == 'POST':
        username = request.user.username
        repo_meta = {
            'name': request.POST['name'],
            'description': request.POST['description'],
            'visibility': request.POST['visibility'],
        }
        # TODO: add file when create repo
        add_file = request.POST.getlist('add_file')

        gitlab_user = gitlab_inst.users.list(username=username)[0]
        user_project = gitlab_user.projects.create(repo_meta)
        # TODO: error message tips
        if user_project is None:
            raise Exception('repo create error.')

        # 建置 Jenkins Job (Multibranch Pipeline)
        job_name = get_job_name(username, repo_meta['name'])
        if jenkins_inst.job_exists(job_name):
            raise Exception('job already exists.')
        gitlab_webhook_url = f"{gitlab_url}/{username}/{repo_meta['name']}"
        config_xml = CONFIG_XML.replace('set_remote', gitlab_webhook_url)
        jenkins_inst.create_job(job_name, config_xml)

        # 建立 GitLab webhook
        jenkins_webhook_url = f'{jenkins_url}/project/{job_name}'
        gitlab_webhook = {
            'url': jenkins_webhook_url,
            'push_events': 1,
            'merge_requests_events': 1,
        }
        project = gitlab_inst.projects.get(user_project.id)
        if project.hooks.list():
            raise Exception('webhook in github already exists.')
        project.hooks.create(gitlab_webhook)

        return redirect('repo_project', user=username, project=repo_meta['name'])

    return render(request, 'repo/repo_new.html', {'form': form})
