from django import template

register = template.Library()

@register.filter(name="description_show")
def description_show(content):
    if len(content)==0:
        return "(Currently has no description.)"
    else:
        return content