from functools import wraps

from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.models import User

from core.dicts import MESSAGE_DICT
from ..models import Role


def get_roles(user: User):
    roles = []
    for role in Role:
        if hasattr(user, role.name.lower()):
            roles.append(role)
    return roles


def check_role(white_list):
    def view_decorator(view_func):
        @wraps(view_func)
        def _wrap(request, *args, **kwargs):
            roles = get_roles(request.user)
            # 使用者身份與白名單有交集
            if not (set(roles) & set(white_list)):
                messages.error(request, MESSAGE_DICT.get('check_role_failed'))
                return redirect('index')
            else:
                return view_func(request, *args, **kwargs)
        return _wrap
    return view_decorator
