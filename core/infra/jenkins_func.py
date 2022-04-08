# functools
import requests

from . import JENKINS_URL, JENKINS_AUTH


def get_job_name(user, project, branch=''):
    # multibranch pipline 專案實際上比較像 "每個分支一個 job 的 folder"
    # 因此如果給定 branch name, job_name 要把原本 job_name 當成 folder, 再加上分支名稱
    if branch:
        return f'{user}_{project}/{branch}'
    else:
        return f'{user}_{project}'


def get_junit_result(user, project, branch, build_no):

    junit = {}
    job_name = get_job_name(user, project)

    # 使用 api 獲得 junit 的結果 (失敗/跳過/總計)
    api_url = f'{JENKINS_URL}/job/{job_name}/job/{branch}/{build_no}/api/json'
    response = requests.get(api_url, auth=JENKINS_AUTH)

    # 確認 api 接收成功
    if response.status_code == 200:
        api_json = response.json()
        # 尋找 junit 的結果
        actions = api_json['actions']
        for action in actions:
            if '_class' in action.keys() and action['_class'] == 'hudson.tasks.junit.TestResultAction':
                junit.update({
                    'fail': action['failCount'],
                    'skip': action['skipCount'],
                    'total': action['totalCount'],
                })
                junit.update({
                    'success': junit['total'] - junit['fail'] - junit['skip'],
                })
                return junit
    return junit
