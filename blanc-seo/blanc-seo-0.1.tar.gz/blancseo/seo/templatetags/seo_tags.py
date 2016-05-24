from django import template
from django.contrib.contenttypes.models import ContentType
from blancseo.seo.models import MetaContent

register = template.Library()


@register.assignment_tag
def get_object_metacontent(obj):
    content_type = ContentType.objects.get_for_model(obj)

    try:
        return MetaContent.objects.get(content_type=content_type, object_id=obj.pk)
    except MetaContent.DoesNotExist:
        pass

    return None
