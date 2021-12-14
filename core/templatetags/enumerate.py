from django import template

register = template.Library()


@register.filter(name='enumerate')
def enumerate_list(items, start=1):
    return enumerate(items, start)
