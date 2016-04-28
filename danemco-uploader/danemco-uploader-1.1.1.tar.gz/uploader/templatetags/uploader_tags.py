from django.template import Library
from ..models import ImageUpload

register = Library()


@register.assignment_tag
def uploader_images(q=None):
    if q:
        return ImageUpload.objects.filter(name__contains=q)
    else:
        return ImageUpload.objects.all()
