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
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-dataprocessing views/forms/actions/components for web ui"""

import json

from cubicweb.predicates import has_related_entities, match_kwargs
from cubicweb.view import EntityView
from cubicweb.web.views import ibreadcrumbs, uicfg


afs = uicfg.autoform_section
pvs = uicfg.primaryview_section
affk = uicfg.autoform_field_kwargs
pvdc = uicfg.primaryview_display_ctrl


afs.tag_object_of(('*', 'process_input_file', 'File'), 'main', 'hidden')


class ScriptImplementationBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    """Define Script / <Implementation> breadcrumbs"""
    __select__ = (ibreadcrumbs.IBreadCrumbsAdapter.__select__ &
                  has_related_entities('implemented_by', role='object'))

    def parent_entity(self):
        return self.entity.reverse_implemented_by[0]


afs.tag_object_of(('*', 'transformation_sequence', 'TransformationSequence'),
                  'main', 'hidden')
afs.tag_object_of(('*', 'validation_script', 'ValidationScript'),
                  'main', 'hidden')
pvdc.tag_attribute(('ValidationScript', 'parameters'), {'vid': 'jsonattr'})
pvdc.tag_attribute(('TransformationStep', 'parameters'), {'vid': 'jsonattr'})


class JSONAttributeView(EntityView):
    """Render an attribute as formatted JSON"""
    __regid__ = 'jsonattr'
    __select__ = EntityView.__select__ & match_kwargs('rtype')

    def entity_call(self, entity, rtype, **kwargs):
        attr = getattr(entity, rtype)
        if attr:
            js = json.dumps(json.loads(attr), indent=2)
            self.w(u'<pre>{0}</pre>'.format(js))


for etype in ('ValidationScript', 'TransformationScript'):
    afs.tag_subject_of((etype, 'implemented_by', '*'), 'main', 'inlined')
    pvs.tag_attribute((etype, 'name'), 'hidden')

afs.tag_object_of(('*', 'in_sequence', 'TransformationSequence'),
                  'main', 'inlined')

for etype in ('DataTransformationProcess', 'DataValidationProcess'):
    uicfg.indexview_etype_section[etype] = 'subobject'
    afs.tag_subject_of((etype, 'process_input_file', '*'),
                       'main', 'attributes')
    pvs.tag_subject_of((etype, 'process_input_file', '*'), 'attributes')
    affk.set_fields_order(etype, ('name', 'description',
                                  ('process_input_file', 'subject')))
