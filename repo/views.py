from datetime import datetime
from pathlib import PurePosixPath
from base64 import b64decode

from django.shortcuts import render, redirect
from django.utils import timezone

from core.utils import CONFIG_XML
from ci.jenkins import jenkins_inst, jenkins_url
from .gitlab import gitlab_inst, gitlab_url
from .utils import timedelta_str, get_repo_verbose, get_tree
from .forms import RepoForm, DelRepoForm


def repo_list_view(request, user):
    """儲存庫列表"""
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
            'last_activity_at': timedelta_str(now_last_delta.seconds),
            'branch_sum': len(branch_list),
        }
    return render(request, 'repo/repo_list.html', {'projects': projects})


def repo_view(request, user, project):
    """檢視儲存庫"""
    form = DelRepoForm(request.POST or None)

    full_project_name = f'{user}/{project}'
    if request.method == 'POST':
        if request.POST['project_info'] == full_project_name:
            gitlab_inst.projects.get(full_project_name).delete()

            # 刪除 Jenkins Job
            job_name = f'{user}_{project}'
            if jenkins_inst.get_job_name(job_name):
                jenkins_inst.delete_job(job_name)
            return redirect('repo_list', user=user)
        else:
            # todo: 輸入錯誤的提示
            pass

    project_info = get_repo_verbose(user, project)

    if project_info['branch_sum'] == 0:
        folders = ''
        files = ''
        root_path = ''
    else:
        folders, files = get_tree(user, project)
        root_path = f'{project}/'

    content = {
        'info': project_info,
        'root_path': root_path,
        'folders': folders,
        'files': files,
        'form': form
    }
    return render(request, 'repo/repository.html', content)


def repo_tree_view(request, user, project, path):
    """儲存庫專案資料夾"""
    project_info = get_repo_verbose(user, project)
    folders, files = get_tree(user, project, path)
    tree_path = request.path.split('tree/')[1]

    content = {
        'info': project_info,
        'tree_path': tree_path,
        'folders': folders,
        'files': files
    }
    return render(request, 'repo/repo_tree.html', content)


def repo_blob_view(request, user, project, path):
    """儲存庫專案檔案"""
    url_as_path = PurePosixPath(path)
    blob_path = str(url_as_path.parent)
    file = url_as_path.name

    project_inst = gitlab_inst.projects.get(f'{user}/{project}')
    project_info = get_repo_verbose(user, project)
    trees = project_inst.repository_tree(path=blob_path)

    for tree in trees:
        if tree['type'] == 'blob' and tree['name'] == file:
            blob = project_inst.repository_blob(tree['id'])
            file = {
                'name': tree['name'],
                'content': b64decode(blob['content']).decode('utf-8'),
            }

    if file['content'] == '':
        line = 0
    elif file['content'][-1] == '\n':
        line = file['content'].count('\n')
    else:
        line = file['content'].count('\n') + 1

    return render(request, 'repo/repo_blob.html', {
        'info': project_info,
        'blob_path': blob_path,
        'file': file,
        'line': line
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
        job_name = f"{username}_{repo_meta['name']}"
        if job_name == jenkins_inst.get_job_name(job_name):
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
