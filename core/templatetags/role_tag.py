from django import template
from django.http import HttpRequest

from accounts.models import Role
from accounts.utils.check_role import get_roles

register = template.Library()


@register.simple_tag
def is_student(request):
    if Role.STUDENT in get_roles(request.user):
        return isinstance(request, HttpRequest) and request.user.is_authenticated and Role.STUDENT


@register.simple_tag
def is_teacher(request):
    if Role.TEACHER in get_roles(request.user):
        return isinstance(request, HttpRequest) and request.user.is_authenticated and Role.TEACHER
