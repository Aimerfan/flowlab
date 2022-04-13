import os
import logging
from datetime import datetime
from pathlib import PurePosixPath
from pkgutil import get_data

from gitlab.exceptions import GitlabGetError

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_http_methods

from core.infra import GITLAB_
from core.infra.gitlab_func import timedelta_str, get_repo_verbose, get_tree
from core.infra import JENKINS_
from core.infra.jenkins_func import get_job_name
from core.infra import SONAR_
from core.infra.sonarqube_func import get_project_name
from core.dicts import MESSAGE_DICT
from ..forms import BlankRepoForm, TemplateRepoForm, ExportTemplateForm
from ..models import Teacher, Template, Project
from ..utils import export_template, import_template, create_jenkins_job, create_gitlab_webhook

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

    # 模板 form
    form = ExportTemplateForm(request.POST or None)
    # 按下匯出模板按鈕
    if request.method == 'POST':
        project_name = request.POST['project']
        template_name = request.POST['name']
        teacher = Teacher.objects.get(user=request.user)

        if Template.objects.filter(teacher=teacher, name=template_name):
            # 模板名稱重複
            messages.warning(request, MESSAGE_DICT.get('template_name_exist').format(template_name))
        else:
            # 匯出模板
            form.instance.template = export_template(user, project_name, template_name)
            form.instance.teacher = teacher
            form.save()
            messages.success(request, MESSAGE_DICT.get('export_template').format(template_name))

            return redirect('template')

    content = {
        'form': form,
        'projects': projects,
    }

    return render(request, 'repo/repo_list.html', content)


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

        # 刪除 SonarQube project
        project_name = get_project_name(user, project)
        SONAR_.projects.delete_project(project=project_name)

        # 刪除 Project model
        Project.objects.get(user=request.user, name=project).delete()
        messages.success(request, MESSAGE_DICT.get('delete_project_success').format(project))
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
        content = content.split('\n')

    blob.update({
        'name': full_path.name,
        'content': content,
        'format': full_path.name.rsplit('.')[-1]
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
        create_jenkins_job(username=username, repo_name=repo_name)
        # 建立 GitLab webhook
        create_gitlab_webhook(username=username, repo_name=repo_name, project=user_project)
        # 建立 SonarQube project
        project_name = get_project_name(username, repo_name)
        SONAR_.projects.create_project(project=project_name, name=project_name)
        # 建立 Project model
        Project.objects.create(user=request.user, name=repo_name)

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
        parent_package = str(__name__).rsplit('.', 2)[0]
        template_path = f'resources/repo_templates/{selected_template}'
        template = get_data(parent_package, template_path)

        # 將模板匯入專案
        project = import_template(
            username=username,
            repo_name=repo_name,
            template_file=template,
            description=form.cleaned_data['description'],
            visibility=form.cleaned_data['visibility'],
        )

        # 建立 Jenkins Job (Multibranch Pipeline 模板)
        create_jenkins_job(username=username, repo_name=repo_name)
        # 建立 GitLab webhook
        create_gitlab_webhook(username=username, repo_name=repo_name, project=project)
        # 建立 SonarQube project
        project_name = get_project_name(username, repo_name)
        SONAR_.projects.create_project(project=project_name, name=project_name)
        # 建立 Project model
        Project.objects.create(user=request.user, name=repo_name)

        return redirect('repo_project', user=username, project=repo_name)

    return render(request, 'repo/repo_new_template.html', {'form': form})


def template_list(request):
    """模板列表"""
    teacher = Teacher.objects.get(user=request.user)
    templates = Template.objects.filter(teacher=teacher)

    form = ExportTemplateForm(request.POST or None)
    if request.method == 'POST' and request.POST['action'] == 'Rename':
        origin_name = request.POST['origin_name']
        new_name = request.POST['name']
        # 修改模板名稱與實際檔案名稱
        template = Template.objects.get(teacher=teacher, name=origin_name)
        origin_path = template.template.path
        new_path = origin_path.replace(origin_name, new_name)
        os.rename(origin_path, new_path)
        template.name = new_name
        template.template = new_path
        template.save()

        messages.success(request, MESSAGE_DICT.get('rename_template').format(new_name))
        return redirect('template')

    elif request.method == 'POST' and request.POST['action'] == 'Delete':
        name = request.POST['name']
        # 刪除模板 model 與實際檔案
        template = Template.objects.get(teacher=teacher, name=name)
        file_path = template.template.path
        os.remove(file_path)
        template.delete()

        messages.success(request, MESSAGE_DICT.get('delete_template').format(name))
        return redirect('template')

    content = {
        'templates': templates,
        'form': form,
    }

    return render(request, 'repo/template_list.html', content)
