from django import template

register = template.Library()

@register.filter(name="get_author_detail")
def get_author_detail(author_link):
    return "Detail/" + author_link[-24:]