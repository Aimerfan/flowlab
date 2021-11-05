import os
import jenkins

from gitlab import Gitlab
from jenkins import Jenkins

from django.shortcuts import render, redirect

from core.utils import ENVIRON
from vcs_adapter import GitLabAdapter
from repo.utils import get_repo_title, get_tree
from .forms import RepoForm, DelRepoForm

"""新增一個共用的 GitLab Instance"""
gitlab_inst = None
try:
    gitlab_url = f'http://{ENVIRON["GITLAB_HOST"]}:{ENVIRON["GITLAB_HTTP_PORT"]}'
    root_token = ENVIRON.get('GITLAB_ROOT_PRIVATE_TOKEN', None)
except KeyError:
    raise KeyError("'GITLAB_HTTP_PORT' or 'GITLAB_HOST' attr. dose not exist in .env file.")
else:
    gitlab_inst = Gitlab(gitlab_url, root_token)
    del root_token

"""新增一個共用的 Jenkins Instance"""
jenkins_inst = None
try:
    jenkins_url = f'http://{ENVIRON["JENKINS_HOST"]}:{ENVIRON["JENKINS_PORT"]}'
except KeyError:
    raise KeyError("'JENKINS_HOST' or 'JENKINS_PORT' attr. dose not exist in .env file.")
else:
    jenkins_inst = Jenkins(jenkins_url, username=ENVIRON['JENKINS_ROOT_USERNAME'], password=ENVIRON['JENKINS_ROOT_PASSWORD'])


def repo_list_view(request, user):
    """儲存庫列表"""
    gl = GitLabAdapter()
    projects = gl.get_repo_list(user)
    for project, info in projects.items():
        br_list = gl.get_branches_list(user, project)
        info['branch_sum'] = len(br_list)

    return render(request, 'repo/repo_list.html', {'projects': projects})


def repo_view(request, user, project):
    """檢視儲存庫"""
    form = DelRepoForm(request.POST or None)

    full_project_name = f'{user}/{project}'
    if request.method == 'POST':
        if request.POST['project_info'] == full_project_name:
            job_name = f'{user}_{project}'

            project = gitlab_inst.projects.get(full_project_name)
            project.delete()

            # 刪除 Jenkins Job
            print(job_name)
            print('----------')
            if jenkins_inst.get_job_name(job_name) is None:
                raise Exception('job does not exist.')
            jenkins_inst.delete_job(job_name)
            return redirect('repo_list', user=user)
        else:
            # todo: 輸入錯誤的提示
            pass

    project_info = get_repo_title(user, project)

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


def repo_tree_view(request, user, project, file):
    """儲存庫專案資料夾"""
    project_info = get_repo_title(user, project)
    folders, files = get_tree(user, project, file)
    tree_path = request.path.split('tree/')[1]

    return render(request, 'repo/repo_tree.html', {'info': project_info, 'tree_path': tree_path, 'folders': folders,
                                                   'files': files})


def repo_blob_view(request, user, project, file):
    """儲存庫專案檔案"""
    gl = GitLabAdapter()
    project_info = get_repo_title(user, project)

    blob_path = os.path.split(file)[0]
    file = os.path.split(file)[1]
    trees = gl.get_tree(user, project, blob_path)
    print(blob_path, file)

    for tree in trees:
        if tree['type'] == 'blob' and tree['name'] == file:
            blob = gl.get_blob(user, project, tree['id'])
            file = {
                'name': tree['name'],
                'content': blob['content'].decode('utf-8'),
            }

    if file['content'] == '':
        line = 0
    elif file['content'][-1] == '\n':
        line = file['content'].count('\n')
    else:
        line = file['content'].count('\n') + 1

    return render(request, 'repo/repo_blob.html', {'info': project_info, 'blob_path': blob_path, 'file': file,
                                                   'line': line})


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

        # 建置 Jenkins Job
        job_name = f"{username}_{repo_meta['name']}"
        if job_name == jenkins_inst.get_job_name(job_name):
            raise Exception('job already exists.')
        jenkins_inst.create_job(job_name, jenkins.EMPTY_CONFIG_XML)
        jenkins_inst.build_job(job_name)

        return redirect('repo_project', user=username, project=repo_meta['name'])

    return render(request, 'repo/repo_new.html', {'form': form})
