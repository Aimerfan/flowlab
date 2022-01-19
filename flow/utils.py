import os
from pkgutil import get_data
from xml.etree import ElementTree
from base64 import b64decode
from time import sleep

from django.views.decorators.csrf import csrf_exempt

from core.infra import ENVIRON
from core.infra import GITLAB_, GITLAB_URL
from core.infra import JENKINS_, JENKINS_URL
from core.infra.jenkins_func import get_job_name
from flowlab.settings import MEDIA_ROOT


def load_multibranch_xml():
    """
    載入 {project_root}/ci/static/ci/multibranch_config.xml
    並轉換為 python String
    """
    config_file = get_data(__name__, 'resources/multibranch_config.xml').decode('utf-8')
    xml = ElementTree.fromstring(config_file)
    xml = ElementTree.tostring(xml).decode()
    xml = xml.replace('set_username', ENVIRON['GITLAB_ROOT_USERNAME'])
    xml = xml.replace('set_password', ENVIRON['GITLAB_ROOT_PASSWORD'])
    return xml


"""Jenkins Multibranch Jobs 預設模板設定"""
CONFIG_XML = load_multibranch_xml()


@csrf_exempt
def update_jenkinsfile(repo_name, selected_branch, selected_tests):
    # Gradle 模板提供的測試
    all_tests = ['unit_test', 'coverage', 'sonarqube']

    # 修改 Jenkinsfile 需要的變數
    modify = False
    is_used = False
    used_stage = f"when {{ branch '{selected_branch}' }}"
    unused_stage = f"when {{ not {{ branch '{selected_branch}' }} }}"

    # 取得專案根目錄下的 Jenkinsfile
    project_inst = GITLAB_.projects.get(repo_name)
    # TODO: 處理根目錄無 Jenkisfile 的狀況
    file = project_inst.files.get(file_path='Jenkinsfile', ref=selected_branch)
    content = b64decode(file.content).decode('utf-8')
    lines = content.split('\n')

    # 根據選擇的分支與測試修改 Jenkinsfile
    for index, line in enumerate(lines):

        # 檢查 stage 是否為模板提供, 是否被選擇
        if 'stage' in line and not 'stages' in line:
            stage_name = line.split("'")[1]
            # stage 被選擇, 採用此 stage
            if stage_name in selected_tests:
                modify = True
                is_used = True
                continue
            # 模板提供的 stage 未被選擇, 不採用此 stage
            elif stage_name in all_tests:
                modify = True
                is_used = False
                continue

        # 屬於模板專案的 stage, 需修改 when 條件
        if modify:
            blank = line.split('when')[0]
            if is_used:
                lines[index] = blank + used_stage
            else:
                lines[index] = blank + unused_stage
            modify = False

    # 組合 Jenkinsfile 內容 (list to string)
    return '\n'.join(lines)


@csrf_exempt
def push_jenkinsfile(repo_name, selected_branch, pipe_content):
    # 取得專案根目錄下的 Jenkinsfile
    project_inst = GITLAB_.projects.get(repo_name)
    file = project_inst.files.get(file_path='Jenkinsfile', ref=selected_branch)

    # push 更新後的 Jenkinsfile 至 GitLab
    file.content = pipe_content
    file.save(branch=selected_branch, commit_message='改變檢測項目')


def export_template(user, project, template_name):
    """匯出 project 作為模板"""
    # 建立匯出模板
    exp_project = GITLAB_.projects.get(f'{user}/{project}')
    export = exp_project.exports.create()

    # 等待 'finished' 狀態
    export.refresh()
    while export.export_status != 'finished':
        sleep(1)
        export.refresh()

    # 指定存放路徑, 檢查是否有資料夾
    template_path = f'{MEDIA_ROOT}/templates/{user}'
    if not os.path.exists(MEDIA_ROOT):
        os.mkdir(MEDIA_ROOT)
    if not os.path.exists(f'{MEDIA_ROOT}/templates'):
        os.mkdir(f'{MEDIA_ROOT}/templates')
    if not os.path.exists(template_path):
        os.mkdir(template_path)

    # 下載結果
    with open(f'{template_path}/{template_name}.tar.gz', 'wb') as f:
        export.download(streamed=True, action=f.write)

    # FIXME: 路徑可能有些問題
    return f'{template_path}/{template_name}.tar.gz'


def import_template(username, repo_name, template_file, description, visibility):
    """
    使用模板建立 (gitlab) project
    return GITLAB_ project instance
    """
    # 匯入到 gitlab
    output = GITLAB_.projects.import_project(
        file=template_file,
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
    created_project.description = description
    created_project.visibility = visibility
    created_project.save()

    return created_project


def create_jenkins_job(username, repo_name):
    """建立 Jenkins Job (使用 Multibranch Pipeline 模板)"""
    job_name = get_job_name(username, repo_name)
    if JENKINS_.job_exists(job_name):
        raise Exception('job already exists.')
    gitlab_repo_url = f"{GITLAB_URL}/{username}/{repo_name}"
    config_xml = CONFIG_XML.replace('set_remote', gitlab_repo_url)
    JENKINS_.create_job(job_name, config_xml)


def create_gitlab_webhook(username, repo_name, project):
    """建立 GitLab webhook (Jenkins 與 GitLab 間)"""
    job_name = get_job_name(username, repo_name)
    jenkins_webhook_url = f'{JENKINS_URL}/project/{job_name}'
    gitlab_webhook = {
        'url': jenkins_webhook_url,
        'push_events': 1,
        'merge_requests_events': 1,
    }
    project = GITLAB_.projects.get(project.id)
    if project.hooks.list():
        raise Exception('webhook in github already exists.')
    project.hooks.create(gitlab_webhook)
