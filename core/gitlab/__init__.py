from gitlab import Gitlab

from core.config import ENVIRON

"""共用的 GitLab Instance"""
inner_gitlab_url = f'http://{ENVIRON["GITLAB_HOST"]}:{ENVIRON["GITLAB_HTTP_PORT"]}'
_root_token = ENVIRON.get('GITLAB_ROOT_PRIVATE_TOKEN')
inner_gitlab = Gitlab(inner_gitlab_url, _root_token)
del _root_token
