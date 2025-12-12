# exams/templatetags/dict_extras.py
from django import template
register = template.Library()

@register.filter
def dictget(dictionary, key):
    return dictionary.get(key)
