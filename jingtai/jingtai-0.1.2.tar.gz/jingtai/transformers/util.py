import re

import yaml


def split_markup(markup):
    """
    Given some markup, return a tuple containing the decoded data and the
    template code.
    """
    match = re.search(r'\n={3,}\n', markup)
    if match:
        start, end = match.span()
        ctx = yaml.load(markup[:start])
        template_code = markup[end:]
    else:
        ctx = {}
        template_code = markup

    return ctx, template_code
