# coding: utf-8

from django import template
from django.utils import timezone

register = template.Library()


@register.filter(name='timestamp')
def timestamp(now):
    return timezone.now().timestamp()
