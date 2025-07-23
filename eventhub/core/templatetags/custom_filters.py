from django import template

register = template.Library()

@register.filter
def split_lines(value):
    return value.splitlines()



@register.filter
def split_keypoint(value):
    """
    Splits a string at the first colon into (title, description).
    Example: 'Security: On-site guards' -> ['Security', 'On-site guards']
    """
    if ':' in value:
        return value.split(':', 1)
    return [value, '']
