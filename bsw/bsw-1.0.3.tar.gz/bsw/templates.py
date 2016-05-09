"""bsw template handling functions"""

import os

template_cache = {}


def get_template(path):
    """Return template body (cached)"""
    if path not in template_cache:
        with open(os.path.join(".", "templates", path), "r") as template_file:
            template_cache[path] = template_file.read()
    return template_cache[path]


def check_templates_exist(pages):
    """Checks that all templates exist, raises FileNotFoundError if missing"""
    for page in pages:
        if "template" in page.page_vars:
            template_path = os.path.join(".", "templates",
                                page.page_vars["template"])
            if not os.path.exists(template_path):
                raise FileNotFoundError(
                    "Template '{0}' for page {1} not found".format(
                        template_path,
                        page.filename))
