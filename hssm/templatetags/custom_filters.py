from django import template

register = template.Library()


@register.filter
def first(value):
    return value[0]


@register.filter
def subtract(value, second):
    return value - second
