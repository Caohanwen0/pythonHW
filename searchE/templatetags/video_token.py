from django import template

register = template.Library()

@register.filter(name="video_token")
def video_token(video_url):
    return video_url[-11:]