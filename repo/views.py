import os

from django.shortcuts import render

from vcs_adapter import GitLabAdapter
from repo.utils import get_repo_title, get_tree


def repo_list_view(request, user):
    """儲存庫專案列表"""
    gl = GitLabAdapter()
    projects = gl.get_repo_list(user)
    for project, info in projects.items():
        br_list = gl.get_branches_list(user, project)
        info['branch_sum'] = len(br_list)

    return render(request, 'repo/repo_list.html', {'projects': projects})


def repo_view(request, user, project):
    """儲存庫專案"""
    project_info = get_repo_title(user, project)
    folders, files = get_tree(user, project)
    root_path = f'{project}/'

    return render(request, 'repo/repository.html', {'info': project_info, 'root_path': root_path, 'folders': folders, 'files': files})


def repo_tree_view(request, user, project, file):
    """儲存庫專案資料夾"""
    project_info = get_repo_title(user, project)
    folders, files = get_tree(user, project, file)
    tree_path = request.path.split('tree/')[1]

    return render(request, 'repo/repo_tree.html', {'info': project_info, 'tree_path': tree_path, 'folders': folders, 'files': files})


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

    return render(request, 'repo/repo_blob.html', {'info': project_info, 'blob_path': blob_path, 'file': file, 'line': line})
