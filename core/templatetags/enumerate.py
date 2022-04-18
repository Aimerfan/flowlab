from django import template

register = template.Library()


@register.filter(name='enumerate')
def enumerate_list(items, start=1):
    """
    含有索引的 for 迴圈, 預設索引從 1 開始
    在 python 中可表示成:
    for index, item in enumerate(items, start=1)
    用法:
    in django template: for index, item in items|enumerate
    in django template with start=0: for index, item in items|enumerate:0
    """
    return enumerate(items, start)
