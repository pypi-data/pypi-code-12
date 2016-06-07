"""bootstrap implementation of forms

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"


from cubicweb.web.views.forms import FieldsForm
from cubicweb.web.views.autoform import AutomaticEntityForm


# Forms
FieldsForm.needs_js += ('cubes.bootstrap.edition.js',)
FieldsForm.needs_css = ()
FieldsForm.cssclass = AutomaticEntityForm.cssclass = 'form-horizontal'
