from datetime import datetime

from gitlab import Gitlab

from django.utils import timezone

from . import GITLAB_


def timedelta_str(seconds):
    """將相差秒數轉換為描述字串"""
    # 時間單位與使用該單位的秒數上限
    unit_dict = {
        'second': 60,
        'minute': 60 * 60,
        'hour': 60 * 60 * 24,
        'day': 60 * 60 * 24 * 7,
        'week': 60 * 60 * 24 * 7 * 4,
        'month': 60 * 60 * 24 * 30 * 12,
        'year': None
    }
    prev_max = 1
    for unit, max_sec in unit_dict.items():
        if unit == 'year' or seconds < max_sec:
            redundant = int(seconds // prev_max)
            plural = 's' if redundant > 1 else ''
            return f'Updated {redundant} {unit}{plural} ago'
        else:
            prev_max = max_sec


def get_repo_verbose(user, project, gitlab: Gitlab = GITLAB_):
    """
    合併 project meta info 與 default branch 的部分訊息
    :return: {
        'name': project name (without <username>/),
        'branch_sum': total branches account,
        'branch': default branch name,
        'sha': 7-character width short commit id of default branch last commit
        'auther_name': auther name of default branch last commit
        'last_info': summary line(title) of default branch last commit
        'last_activity_at': commit time of default branch last commit
    }
    """
    project = gitlab.projects.get(f'{user}/{project}')
    branches = project.branches.list()

    project_verbose = {
        'name': project.name,
        'branch_sum': len(branches),
        'branches': branches,
        'branch': project.default_branch,
    }

    for branch in branches:
        if branch.name == project.default_branch:
            project_verbose['sha'] = branch.commit['short_id']

            # origin author_name: 'DESKTOP-15W6XC8\\username'
            author_name = branch.commit['author_name']
            author_name = author_name.split('\\')[-1]
            project_verbose['author_name'] = author_name

            project_verbose['last_info'] = branch.commit['title']

            # convert created time as timedelta
            created_at = datetime.fromisoformat(branch.commit['created_at'])
            delta = timezone.now() - created_at
            project_verbose['last_activity_at'] = timedelta_str(delta.seconds)
            break

    return project_verbose


def get_tree(user, project, path='', ref='', gitlab: Gitlab = GITLAB_):
    project = gitlab.projects.get(f'{user}/{project}')
    trees = project.repository_tree(path=path, ref=ref)

    folders = {}
    files = {}
    # TODO: 填充單個檔案的 last_info 與 last_time
    for tree in trees:
        sub_tree = {
            'id': tree['id'],
            'path': tree['path'],
            'last_info': '',
            'last_time': '',
        }
        if tree['type'] == 'tree':
            folders[tree['name']] = sub_tree
        elif tree['type'] == 'blob':
            files[tree['name']] = sub_tree

    return folders, files
