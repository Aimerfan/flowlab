from gitlab import Gitlab

from core.config import ENVIRON


"""共用的 GitLab Instance"""
GITLAB_URL = f'http://{ENVIRON["GITLAB_HOST"]}:{ENVIRON["GITLAB_HTTP_PORT"]}'
_root_token = ENVIRON.get('GITLAB_ROOT_PRIVATE_TOKEN')
GITLAB_ = Gitlab(GITLAB_URL, _root_token)
del _root_token
