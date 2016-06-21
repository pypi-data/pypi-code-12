import re

from terrapin.lexer import word_regex


def render_simple(template, context):
    """ Render a template by replacing variables """

    return replace_variables(template, context)


def replace_variables(string, variables):
    """ Format a templated value """

    found_variables = find_variables(string)
    for variable in found_variables:
        value = str(variables.get(variable, ''))
        string = string.replace('{{' + variable + '}}', value)
    return string


def find_variables(template):
    """ Find all the used variables

    This is any string that looks like {{var}}
    """

    capture_variable_regex = r'\{\{(' + word_regex + r')\}\}'
    found_variables = re.findall(capture_variable_regex, template)
    return list(found_variables)