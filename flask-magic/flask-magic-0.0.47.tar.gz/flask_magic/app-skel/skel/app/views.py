"""
Magic
"""

from flask_magic import (Magic, set_meta, get_config, flash, abort, request,
                         url_for, redirect)
from flask_magic.decorators import (route, menu, template, plugin, methods)
from flask_magic.plugins import (contact_page, )

# ------------------------------------------------------------------------------

@plugin(contact_page.contact_page, menu={"title": "Contact Us", "order": 3})
class Index(Magic):

    @menu("Home", order=1)
    def index(self):
        set_meta(title="Hello View!")
        return {}





