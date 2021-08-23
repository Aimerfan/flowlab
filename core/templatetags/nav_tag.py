from django import template

register = template.Library()


@register.simple_tag
def get_name(request):
    user = request.user
    if user.is_authenticated:
        return user.username
