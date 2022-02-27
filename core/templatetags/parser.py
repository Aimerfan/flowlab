from django import template

register = template.Library()


@register.filter(name='combine')
def combine_topic_options(topic, options):
    """
    組合題目與選項, 以符合評量問題的撰寫語法
    """
    content = topic
    for option in options:
        content += f'() {option}'
    return content
