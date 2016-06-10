from django import template

register = template.Library()


@register.simple_tag
def url_replace(request, field, value):
    '''
    This is handy for generating links in templates where you want to change
    one variable but keep all existing GET request vars.

    Example:
    <a href="?{% url_replace request 'page' page_obj.next_page_number %}">next</a>

    :param request:
    :param field:
    :param value:
    :return:
    '''
    dict_ = request.GET.copy()

    dict_[field] = value

    return dict_.urlencode()
