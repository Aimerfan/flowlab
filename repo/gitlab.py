from gitlab import Gitlab

from core.utils import ENVIRON

"""共用的 GitLab Instance"""
gitlab_url = f'http://{ENVIRON["GITLAB_HOST"]}:{ENVIRON["GITLAB_HTTP_PORT"]}'
_root_token = ENVIRON.get('GITLAB_ROOT_PRIVATE_TOKEN')
gitlab_inst = Gitlab(gitlab_url, _root_token)
del _root_token

"""提供模板專案的 Public GitLab"""
public_gitlab = Gitlab('https://gitlab.com/')
public_gitlab_group = public_gitlab.groups.get('14301860')
