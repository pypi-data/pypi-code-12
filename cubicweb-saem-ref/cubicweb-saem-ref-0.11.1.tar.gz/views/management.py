# copyright 2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""Site management views (handling of Authorities and ARK name assigning authorities among others)
"""

import re

from cubicweb.predicates import has_permission, is_instance
from cubicweb.web import component, formwidgets as fw
from cubicweb.web.views import actions, debug, urlrewrite, uicfg

from cubes.saem_ref.views import SAEMRefRewriter, AddEntityComponent, authority_form_value

_ = unicode
pvs = uicfg.primaryview_section
abaa = uicfg.actionbox_appearsin_addmenu
afs = uicfg.autoform_section
affk = uicfg.autoform_field_kwargs


class ManagementAddEntityComponent(AddEntityComponent):
    __select__ = (component.CtxComponent.__select__ & has_permission('add') &
                  is_instance('Authority', 'ArkNameAssigningAuthority'))


class AutorithyAction(actions.ManagersAction):
    __regid__ = 'authority'
    title = _('authorities')
    order = 1
    category = 'manage'


class ARKNamingAutorithyAction(actions.ManagersAction):
    __regid__ = 'arknameassigningauthority'
    title = _('ARK name assigning authorities')
    order = 2
    category = 'manage'


# Rewrite rules to force "sameetypelist" view for these routes (even if
# there's only one entity).
SAEMRefRewriter.rules += [
    (urlrewrite.rgx('/arknameassigningauthority', re.I),
     {'vid': 'sameetypelist',
      'rql': 'Any X, XN WHERE X who XN, X is ArkNameAssigningAuthority'}),
    (urlrewrite.rgx('/authority', re.I),
     {'vid': 'sameetypelist',
      'rql': 'Any X, XN WHERE X name XN, X is Authority'}),
]

pvs.tag_subject_of(('Authority', 'ark_naa', 'ArkNameAssigningAuthority'), 'attributes')
afs.tag_subject_of(('Authority', 'ark_naa', 'ArkNameAssigningAuthority'), 'main', 'attributes')
pvs.tag_object_of(('*', 'authority', 'Authority'), 'hidden')
afs.tag_object_of(('*', 'authority', 'Authority'), 'main', 'hidden')
abaa.tag_object_of(('*', 'authority', 'Authority'), False)

pvs.tag_subject_of(('*', 'ark_naa', '*'), 'attributes')
afs.tag_subject_of(('*', 'ark_naa', '*'), 'main', 'attributes')
pvs.tag_subject_of(('*', 'authority', '*'), 'attributes')
afs.tag_subject_of(('*', 'authority', '*'), 'main', 'attributes')

affk.set_field_kwargs('Authority', 'name', widget=fw.TextInput({'size': 80}))

affk.tag_subject_of(('*', 'authority', '*'), {'value': authority_form_value})

pvs.tag_object_of(('*', 'ark_naa', 'ArkNameAssigningAuthority'), 'relations')
afs.tag_object_of(('*', 'ark_naa', 'ArkNameAssigningAuthority'), 'main', 'hidden')

affk.set_field_kwargs('ArkNameAssigningAuthority', 'what', widget=fw.TextInput({'size': 80}))


actions.SiteConfigurationAction.order = 100
debug.SiteInfoAction.order = 101
