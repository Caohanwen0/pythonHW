from django import template

register = template.Library()

@register.filter(name="byte_to_str")

def byte_to_str(byt):
    if byt[2:-1]!="":
        return byt[2:-1]
    else:
        return '0'