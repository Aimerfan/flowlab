from datetime import datetime
from functools import wraps
from base64 import b64decode

from gitlab import Gitlab

from django.utils import timezone

from core.utils import ENVIRON
from .base import VCSAdapter


def use_self_attr(cls_method):
    @wraps(cls_method)
    def wrap(self, user=None, repo=None, *args, **kwargs):
        user = user if user is not None else self.user
        repo = repo if repo is not None else self.repo
        return cls_method(self, user, repo, *args, **kwargs)
    return wrap


class GitLabAdapter(VCSAdapter):

    def __init__(self, url=None, token=None, user=None, repo=None):
        if url is None:
            try:
                url = f'http://{ENVIRON["GITLAB_HOST"]}:{ENVIRON["GITLAB_HTTP_PORT"]}'
            except KeyError:
                raise KeyError("'GITLAB_HTTP_PORT' or 'GITLAB_HOST' attr. dose not exist in .env file.")
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
        project = self.gitlab.projects.get(f'{user}/{repo}')
        project_dict = {
            'name': project.name,
            'default_branch': project.default_branch,
        }
        return project_dict

    @use_self_attr
    def get_branches_list(self, user, repo):
        project = self.gitlab.projects.get(f'{user}/{repo}')
        branches = project.branches.list()
        br_list = []
        for br in branches:
            # origin author_name: 'DESKTOP-15W6XC8\\username'
            author_name = br.commit['author_name']
            author_name = author_name.split('\\')[-1]
            # convert created time as timedelta
            created_at = datetime.fromisoformat(br.commit['created_at'])
            delta = timezone.now() - created_at

            br_list.append({
                'name': br.name,
                'default': br.default,
                'commit': {
                    'short_id': br.commit['short_id'],
                    'title': br.commit['title'],
                    'author_name': author_name,
                    'last_activity_at': GitLabAdapter.timedelta_str(delta.seconds),
                },
            })
        return br_list

    @use_self_attr
    def get_commit(self, user, repo, branch):
        pass

    @use_self_attr
    def get_tree(self, user, repo, path=None, ref=None):
        project = self.gitlab.projects.get(f'{user}/{repo}')
        return project.repository_tree(path=path, ref=ref)

    @use_self_attr
    def get_blob(self, user, repo, blob_sha):
        project = self.gitlab.projects.get(f'{user}/{repo}')
        blob = project.repository_blob(blob_sha)
        return {
            'size': blob['size'],
            'content': b64decode(blob['content']),
        }
