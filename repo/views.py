from django.shortcuts import render


def repo_list_view(request, user):
    """儲存庫專案列表"""
    print(request.user)
    print(user)
    project_info = {
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
    return render(request, 'repo/repo_list.html', {'project_info': project_info})


def repo_view(request, user, project):
    """儲存庫專案"""
    print(request.user)
    print(user, project)
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
        '.env': {
            'name': '.env',
            'last_info': 'chore',
            'last_time': '10 days ago',
        },
        'main.py': {
            'name': 'main.py',
            'last_info': 'feat',
            'last_time': '1 day ago',
        },
        'app': {
            'name': 'app',
            'last_info': 'feat',
            'last_time': '4 days ago',
        },
    }
    return render(request, 'repo/repository.html', {'info': project_info, 'files': files})
