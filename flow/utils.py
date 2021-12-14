from pkgutil import get_data
from xml.etree import ElementTree
from base64 import b64decode

from django.views.decorators.csrf import csrf_exempt

from core.infra import ENVIRON
from core.infra import GITLAB_


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
