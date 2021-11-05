from gitlab import Gitlab

from core.utils import ENVIRON

"""共用的 GitLab Instance"""
gitlab_url = f'http://{ENVIRON["GITLAB_HOST"]}:{ENVIRON["GITLAB_HTTP_PORT"]}'
root_token = ENVIRON.get('GITLAB_ROOT_PRIVATE_TOKEN')
gitlab_inst = Gitlab(gitlab_url, root_token)
del root_token
