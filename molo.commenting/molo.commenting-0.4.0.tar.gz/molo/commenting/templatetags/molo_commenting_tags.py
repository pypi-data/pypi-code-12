from django import template
from django.contrib.contenttypes.models import ContentType

from molo.commenting.models import MoloComment

# NOTE: heavily inspired by
#       https://github.com/santiagobasulto/django-comments-utils


register = template.Library()


def get_molo_comments(parser, token):
    """
    Get a limited set of comments for a given object.
    Defaults to a limit of 5. Setting the limit to -1 disables limiting.

    usage:

        {% get_molo_comments for object as variable_name %}
        {% get_molo_comments for object as variable_name limit amount %}

    """
    keywords = token.contents.split()
    if len(keywords) != 5 and len(keywords) != 7:
        raise template.TemplateSyntaxError(
            "'%s' tag takes exactly 2 or 4 arguments" % (keywords[0],))
    if keywords[1] != 'for':
        raise template.TemplateSyntaxError(
            "first argument to '%s' tag must be 'for'" % (keywords[0],))
    if keywords[3] != 'as':
        raise template.TemplateSyntaxError(
            "first argument to '%s' tag must be 'as'" % (keywords[0],))
    if len(keywords) > 5 and keywords[5] != 'limit':
        raise template.TemplateSyntaxError(
            "third argument to '%s' tag must be 'limit'" % (keywords[0],))
    if len(keywords) > 5:
        return GetMoloCommentsNode(keywords[2], keywords[4], keywords[6])
    return GetMoloCommentsNode(keywords[2], keywords[4])


class GetMoloCommentsNode(template.Node):

    def __init__(self, obj, variable_name, limit=5):
        self.obj = obj
        self.variable_name = variable_name
        self.limit = int(limit)

    def render(self, context):
        try:
            obj = template.resolve_variable(self.obj, context)
        except template.VariableDoesNotExist:
            return ''

        qs = MoloComment.objects.for_model(obj.__class__).filter(
            object_pk=obj.pk, parent__isnull=True)
        if self.limit > 0:
            qs = qs[:self.limit]
        qs = [c.get_descendants(include_self=True) for c in qs]
        context[self.variable_name] = qs
        return ''


def get_comments_content_object(parser, token):
    """
    Get a limited set of comments for a given object.
    Defaults to a limit of 5. Setting the limit to -1 disables limiting.

    usage:

        {% get_comments_content_object for form_object as variable_name %}

    """
    keywords = token.contents.split()
    if len(keywords) != 5:
        raise template.TemplateSyntaxError(
            "'%s' tag takes exactly 2 arguments" % (keywords[0],))
    if keywords[1] != 'for':
        raise template.TemplateSyntaxError(
            "first argument to '%s' tag must be 'for'" % (keywords[0],))
    if keywords[3] != 'as':
        raise template.TemplateSyntaxError(
            "first argument to '%s' tag must be 'as'" % (keywords[0],))
    return GetCommentsContentObject(keywords[2], keywords[4])


class GetCommentsContentObject(template.Node):

    def __init__(self, obj, variable_name):
        self.obj = obj
        self.variable_name = variable_name

    def render(self, context):
        try:
            form = template.resolve_variable(self.obj, context)
        except template.VariableDoesNotExist:
            return ''

        app_label, model = form['content_type'].value().split('.')
        object_pk = form['object_pk'].value()

        content_type = ContentType.objects.get(app_label=app_label,
                                               model=model)

        context[self.variable_name] = content_type.get_object_for_this_type(
            pk=object_pk)

        return ''


def is_in_group(user, group_name):
    """
    Check if a user in a group named ``group_name``.
    :param user User:
        The auth.User object
    :param group_name str:
        The name of the group
    :returns: bool
    """
    return user.groups.filter(name__exact=group_name).exists()


register.filter('is_in_group', is_in_group)
register.tag('get_molo_comments', get_molo_comments)
register.tag('get_comments_content_object', get_comments_content_object)
