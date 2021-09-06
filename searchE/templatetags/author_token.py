from django import template

register = template.Library()

@register.filter(name="author_token")
def author_token(author_url):
    return author_url[-24:]