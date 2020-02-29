from django import template

register = template.Library()


@register.simple_tag
def spt(value):
    """Removes all values of arg from the given string"""
    return value.replace('spotify:track:', '')
