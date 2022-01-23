from django import template

register = template.Library()


@register.simple_tag
def set_value(value):
    """更新 template 中已有的變數"""
    return value
