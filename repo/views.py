from django.shortcuts import render


def repo_list_view(request, user):
    """儲存庫專案列表"""
    projects = {
        'flowlab': {
            'name': 'flowlab',
            'last_time': '3 minutes ago',
            'branch_sum': 4,
        },
        'lab': {
            'name': 'lab',
            'last_time': '10 days ago',
            'branch_sum': 1,
        },
    }
    return render(request, 'repo/repo_list.html', {'projects': projects})


def repo_view(request, user, project):
    """儲存庫專案"""
    project_info = {
        'name': 'flowlab',
        'branch_sum': 4,
        'branch': 'master',
        'sha': '78b3472',
        'author_name': 'aimerfan',
        'last_info': 'init commit',
        'last_time': '3 minutes ago',
    }
    files = {
        'app': {
            'name': 'app',
            'format': 'folder',
            'last_info': 'feat',
            'last_time': '4 days ago',
        },
        '.env': {
            'name': '.env',
            'format': 'file',
            'last_info': 'chore',
            'last_time': '10 days ago',
        },
        'main.py': {
            'name': 'main.py',
            'format': 'file',
            'last_info': 'feat',
            'last_time': '1 day ago',
        },
    }
    return render(request, 'repo/repository.html', {'info': project_info, 'files': files})


def repo_tree_view(request, user, project, file):
    """儲存庫專案資料夾"""
    project_info = {
        'name': 'flowlab',
        'branch_sum': 4,
        'branch': 'master',
        'sha': '78b3472',
        'author_name': 'aimerfan',
        'last_info': 'init commit',
        'last_time': '3 minutes ago',
    }
    folder = {
        'front': {
            'last_info': 'init commit',
            'last_time': '2 months ago',
        },
        'server': {
            'last_info': 'init commit',
            'last_time': '2 months ago',
        },
    }
    file = {
        'README.md': {
            'last_info': 'init commit',
            'last_time': '2 months ago',
        },
        'Jenkinsfile': {
            'last_info': 'feat',
            'last_time': '3 minutes ago',
        },
    }
    return render(request, 'repo/repo_tree.html', {'info': project_info, 'folder': folder, 'file': file})


def repo_blob_view(request, user, project, file):
    """儲存庫專案檔案"""
    project_info = {
        'name': 'flowlab',
        'branch_sum': 4,
        'branch': 'master',
        'sha': '78b3472',
        'author_name': 'aimerfan',
        'last_info': 'init commit',
        'last_time': '3 minutes ago',
    }
    file = {
        'name': 'README.md',
        'content': 'README\nflowlab\n一套模擬 DevOps\n與 CI/CD 自動化流程的實驗室。\n',
    }
    line = file['content'].count('\n')
    return render(request, 'repo/repo_blob.html', {'info': project_info, 'file': file, 'line': line})
