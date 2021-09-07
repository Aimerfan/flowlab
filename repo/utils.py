from vcs_adapter import GitLabAdapter


def get_repo_title(user, project):
    gl = GitLabAdapter()
    repo = gl.get_repo(user, project)
    branch_list = gl.get_branches_list(user, project)

    project_info = {
        'name': repo['name'],
        'branch_sum': len(branch_list),
        'branch': repo['default_branch'],
    }

    for branch in branch_list:
        if branch['name'] == repo['default_branch']:
            project_info['sha'] = branch['commit']['short_id']
            project_info['author_name'] = branch['commit']['author_name']
            project_info['last_info'] = branch['commit']['title']
            project_info['last_activity_at'] = branch['commit']['last_activity_at']

    return project_info


def get_tree(user, project, path=None):
    gl = GitLabAdapter()
    if path is None:
        trees = gl.get_tree(user, project)
    else:
        trees = gl.get_tree(user, project, path)

    folders = {}
    files = {}

    # todo: 填充單個檔案的 last_info 與 last_time
    for tree in trees:
        if tree['type'] == 'tree':
            folders[tree['name']] = {
                'id': tree['id'],
                'path': tree['path'],
                'last_info': '',
                'last_time': '',
            }
        elif tree['type'] == 'blob':
            files[tree['name']] = {
                'id': tree['id'],
                'path': tree['path'],
                'last_info': '',
                'last_time': '',
            }

    return folders, files
