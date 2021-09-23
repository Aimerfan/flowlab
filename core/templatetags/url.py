from django import template

from core.utils import ENVIRON

register = template.Library()


@register.simple_tag
def get_gitlab_url(username, project):
    return f'http://{ENVIRON["GITLAB_HOST"]}:{ENVIRON["GITLAB_HTTP_PORT"]}/{username}/{project}.git'


@register.simple_tag
def get_gitlab_ssh(username, project):
    return f'ssh://git@{ENVIRON["GITLAB_HOST"]}:{ENVIRON["GITLAB_SSH_PORT"]}/{username}/{project}.git'
