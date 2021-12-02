from base64 import b64decode

from django.views.decorators.csrf import csrf_exempt

from repo.gitlab import gitlab_inst


@csrf_exempt
def update_jenkinsfile(user, project, selected_branch, selected_tests):
    # Gradle 模板提供的測試
    all_tests = ['unit_test', 'coverage', 'sonarqube']

    # 修改 Jenkinsfile 需要的變數
    modify = False
    is_used = False
    used_stage = f"when {{ branch '{selected_branch}' }}"
    unused_stage = f"when {{ not {{ branch '{selected_branch}' }} }}"

    # 取得專案根目錄下的 Jenkinsfile
    project_inst = gitlab_inst.projects.get(f'{user}/{project}')
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

    # 組合檔案內容 (list to string), 並更新至 Jenkinsfile 上
    file.content = '\n'.join(lines)
    file.save(branch=selected_branch, commit_message='改變檢測項目')
