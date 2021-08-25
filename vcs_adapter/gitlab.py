from datetime import datetime
from functools import wraps

from gitlab import Gitlab

from django.utils import timezone

from core.utils import ENVIRON
from .base import VCSAdapter


def use_self_attr(cls_method):
    @wraps(cls_method)
    def wrap(self, user=None, repo=None, *args, **kwargs):
        user = self.user if self.user is not None else user
        repo = self.repo if self.repo is not None else repo
        return cls_method(self, user, repo, *args, **kwargs)
    return wrap


class GitLabAdapter(VCSAdapter):

    def __init__(self, url=None, token=None, user=None, repo=None):
        if url is None:
            try:
                url = f'http://gitlab:{ENVIRON.GITLAB_HTTP_PORT}'
            except KeyError:
                raise KeyError("'GITLAB_HTTP_PORT' attr dose not exist in .env file.")
        if token is None:
            token = ENVIRON.get('GITLAB_ROOT_PRIVATE_TOKEN', None)
        super().__init__(url, token, user, repo)
        self.gitlab = Gitlab(url, token)

    def get_repo_list(self, username):
        gilab_user = self.gitlab.users.list(username=username)[0]
        repo_list = {}
        for repo in gilab_user.projects.list():
            last_updated = repo.last_activity_at.replace('Z', '+00:00')
            now_last_delta = timezone.now() - datetime.fromisoformat(last_updated)
            repo_list[repo.name] = {
                'last_activity_at': GitLabAdapter.timedelta_str(now_last_delta.seconds),
            }
        return repo_list

    @use_self_attr
    def get_repo(self, user, repo):
        pass

    @use_self_attr
    def get_branches(self, user, repo):
        pass

    @use_self_attr
    def get_commits(self, user, repo, branch):
        pass

    @use_self_attr
    def get_tree(self, user, repo, path=None, ref=None):
        pass

    @use_self_attr
    def get_blob(self, user, repo, blob_sha):
        pass
