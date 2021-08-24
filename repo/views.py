from django.shortcuts import render


def repo_list_view(request, user):
    """儲存庫專案列表"""
    print(request.user)
    print(user)
    project_info = {
        'flowlab': {
            'name': 'flowlab',
            'last_time': '3 minutes ago',
            'branch_sum': '4',
        },
        'lab': {
            'name': 'lab',
            'last_time': '10 days ago',
            'branch_sum': '2',
        },
    }
    return render(request, 'repo/repo_list.html', {'projects': project_info})


def repo_view(request, user, project):
    """儲存庫專案"""
    print(request.user)
    print(user, project)
    return render(request, 'repo/repository.html')
