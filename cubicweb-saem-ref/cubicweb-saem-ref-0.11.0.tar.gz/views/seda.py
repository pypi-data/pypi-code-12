# copyright 2015-2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-saem-ref views related to SEDA"""

from copy import copy, deepcopy
from functools import partial
from collections import defaultdict

from logilab.mtconverter import xml_escape

from cubicweb import tags, uilib, utils, Unauthorized
from cubicweb.view import EntityView
from cubicweb.predicates import (is_instance, score_entity, one_line_rset, multi_lines_rset,
                                 has_permission, match_form_params, has_related_entities,
                                 is_in_state, relation_possible)
from cubicweb.web import (Redirect, httpcache, action, component, controller,
                          formwidgets as fw, formfields as ff)
from cubicweb.web.views import (ibreadcrumbs, idownloadable, uicfg, baseviews,
                                tableview, primary, ajaxcontroller,
                                formrenderers, actions, editforms)

from cubes.relationwidget import views as rwdg
from cubes.compound.entities import copy_entity
from cubes.compound.views import CloneAction

from cubes.saem_ref.views import jqtree
from cubes.saem_ref.views import add_etype_link, configure_relation_widget, index_dropdown_button
from cubes.saem_ref.views.widgets import ConceptAutoCompleteWidget


_ = unicode


# custom widget ####################################################################################

class SEDAMetaFieldMixIn(object):
    """This mix-in is designed to create compound field allowing edition of a `user_annotation` and
    optionaly a `user_cardinality` fields, which appear hidden by default.
    """

    @staticmethod
    def cardinality_field(form):
        """Return the field for `user_cardinality` if the attribute is applyable to the edited
        entity.
        """
        eschema = form.edited_entity.e_schema
        if 'user_cardinality' in eschema.subjrels:
            rschema = eschema.subjrels['user_cardinality']
            return ff.guess_field(eschema, rschema, 'subject', form._cw)
        return None

    @staticmethod
    def annotation_field(form):
        """Return the field for `user_annotation` entity. """
        eschema = form.edited_entity.e_schema
        rschema = eschema.subjrels['user_annotation']
        return ff.guess_field(eschema, rschema, 'subject', form._cw)

    def actual_fields(self, form):
        """Overriden from :class:`Field`"""
        yield self
        card_field = self.cardinality_field(form)
        if card_field:
            yield card_field
        yield self.annotation_field(form)

    def render(self, form, renderer):
        """Overriden from :class:`Field` to render fields in a div which is hidden by default"""
        form._cw.add_js('cubes.saem_ref.js')
        wdgs = [self.get_widget(form).render(form, self, renderer)]
        self._render_hidden_section(wdgs, form, renderer)
        return u'\n'.join(wdgs)

    def _render_hidden_section(self, wdgs, form, renderer):
        divid = '%s-advanced' % self.input_name(form)
        self._render_hidden_section_title(wdgs, form, divid)
        wdgs.append(u'<div id="%s" class="hidden">' % divid)
        card_field = self.cardinality_field(form)
        if card_field:
            wdgs.append(self._render_subfield(form, card_field, renderer))
        wdgs.append(self._render_subfield(form, self.annotation_field(form), renderer))
        wdgs.append(u'</div>')

    @staticmethod
    def _render_hidden_section_title(wdgs, form, divid):
        wdgs.append(tags.a(u'', onclick=unicode(uilib.js.saem.toggleFormMetaVisibility(divid)),
                           href='javascript:$.noop()', title=form._cw._('show meta fields'),
                           klass='icon-list-add'))

    @staticmethod
    def _render_subfield(form, field, renderer):
        """Render a sub-field: label + widget + help + EOL"""
        data = utils.UStringIO()
        w = data.write
        w(u'<div class="row">')
        w(renderer.render_label(form, field))
        w(u'<div class="col-md-9">')
        w(field.render(form, renderer))
        w(u'</div>')
        w(u'</div>')
        w(u'<div class="row">')
        w(u'<div class="col-md-offset-3 col-md-9">')
        w(renderer.render_help(form, field))
        w(u'</div>')
        w(u'</div>')
        return data.getvalue()

    def get_widget(self, form):
        """return the widget instance associated to this field"""
        widget = super(SEDAMetaFieldMixIn, self).get_widget(form)
        widget.attrs['class'] = 'metaField'
        return self.widget


class SEDAMetaField(SEDAMetaFieldMixIn, ff.Field):
    """Field to handle case where the cardinality and annotation fields have not field to which to
    be attached to.
    """

    def __init__(self, *args, **kwargs):
        super(SEDAMetaField, self).__init__(*args, **kwargs)
        # XXX need a space so an empty label is generated and so we get proper fields alignment
        self.label = ' '

    def actual_fields(self, form):
        """Overriden from :class:`SEDAMetaFieldMixIn`"""
        card_field = self.cardinality_field(form)
        if card_field:
            yield card_field
        yield self.annotation_field(form)

    def render(self, form, renderer):
        """Overriden from :class:`Field` to render fields in a div which is hidden by default"""
        form._cw.add_js('cubes.saem_ref.js')
        wdgs = []
        self._render_hidden_section(wdgs, form, renderer)
        return u'\n'.join(wdgs)

    # def _render_hidden_section_title(self, wdgs, form, divid):
    #     wdgs.append(tags.a(form._cw._('show meta fields'),
    #                        onclick=unicode(uilib.js.saem.toggleFormMetaVisibility(divid)),
    #                        href='javascript:$.noop()'))


# primary view configuration #######################################################################

afs = uicfg.autoform_section
pvs = uicfg.primaryview_section
pvds = uicfg.primaryview_display_ctrl

pvs.tag_subject_of(('*', 'seda_appraisal_rule', '*'), 'attributes')
pvs.tag_subject_of(('*', 'seda_access_restriction_code', '*'), 'attributes')
pvs.tag_subject_of(('*', 'seda_content_description', '*'), 'attributes')
pvs.tag_subject_of(('*', 'seda_oldest_date', '*'), 'attributes')
pvs.tag_subject_of(('*', 'seda_latest_date', '*'), 'attributes')
pvs.tag_subject_of(('*', 'seda_description', '*'), 'attributes')
pvs.tag_object_of(('*', 'seda_keyword_of', '*'), 'attributes')
pvs.tag_object_of(('*', 'seda_parent', '*'), 'hidden')
pvs.tag_subject_of(('*', 'seda_document_type_code', '*'), 'attributes')
pvs.tag_subject_of(('*', 'seda_file_type_code', '*'), 'attributes')
pvs.tag_subject_of(('*', 'seda_character_set_code', '*'), 'attributes')
pvs.tag_attribute(('SEDAProfile', 'ark'), 'attributes')

# related SKOS object
pvs.tag_object_of(('*', 'seda_keyword_scheme', '*'), 'hidden')
pvs.tag_subject_of(('ConceptScheme', 'scheme_relation', '*'), 'hidden')
afs.tag_subject_of(('ConceptScheme', 'scheme_relation', '*'), 'main', 'hidden')

# hide default relation components for 'seda_replace' rtype
pvs.tag_subject_of(('*', 'seda_replace', '*'), 'hidden')
pvs.tag_object_of(('*', 'seda_replace', '*'), 'hidden')

# reledit (primary view) configuration #############################################################

rec = uicfg.reledit_ctrl
rec.tag_subject_of(('*', 'seda_name', '*'),
                   {'rvid': 'saem.seda.value'})
rec.tag_subject_of(('*', 'seda_description', '*'),
                   {'rvid': 'saem.seda.value'})
rec.tag_subject_of(('*', 'seda_access_restriction_code', '*'),
                   {'rvid': 'saem.seda.access-restriction-value'})
rec.tag_subject_of(('*', 'seda_appraisal_rule', '*'),
                   {'rvid': 'saem.seda.appraisal-rule-value'})
rec.tag_subject_of(('*', 'seda_content_description', '*'),
                   {'rvid': 'saem.seda.content-description-value'})
rec.tag_subject_of(('*', 'seda_document_type_code', '*'),
                   {'rvid': 'saem.seda.document-type-code-value'})
rec.tag_subject_of(('*', 'seda_file_type_code', '*'),
                   {'rvid': 'saem.seda.file-type-code-value'})
rec.tag_subject_of(('*', 'seda_character_set_code', '*'),
                   {'rvid': 'saem.seda.character-set-code-value'})


class ValueView(EntityView):
    __regid__ = 'saem.seda.value'

    def entity_call(self, entity):
        if entity.value:
            self.wdata(entity.value)
        else:
            self.wdata(self._cw._('<no value>'))


class AccessRestrictionValueView(EntityView):
    __regid__ = 'saem.seda.access-restriction-value'

    def entity_call(self, entity):
        if entity.seda_access_restriction_code_value:
            entity.seda_access_restriction_code_value[0].view('oneline', w=self.w)
        else:
            self.wdata(self._cw._('<no value>'))


class SEDAFileTypeCodeValueView(EntityView):
    __regid__ = 'saem.seda.file-type-code-value'

    def entity_call(self, entity):
        if entity.seda_file_type_code_value:
            entity.seda_file_type_code_value[0].view('saem.concept.alt', w=self.w)
        else:
            self.wdata(self._cw._('<no value>'))


class SEDADocumentTypeCodeValueView(EntityView):
    __regid__ = 'saem.seda.document-type-code-value'

    def entity_call(self, entity):
        if entity.seda_document_type_code_value:
            entity.seda_document_type_code_value[0].view('oneline', w=self.w)
        else:
            self.wdata(self._cw._('<no value>'))


class SEDACharacterSetCodeValueView(EntityView):
    __regid__ = 'saem.seda.character-set-code-value'

    def entity_call(self, entity):
        if entity.seda_character_set_code_value:
            entity.seda_character_set_code_value[0].view('saem.concept.alt', w=self.w)
        else:
            self.wdata(self._cw._('<no value>'))


class AppraisalRuleValueView(EntityView):
    __regid__ = 'saem.seda.appraisal-rule-value'

    def entity_call(self, entity):
        _ = self._cw._
        if (entity.seda_appraisal_rule_duration and
                entity.appraisal_rule_duration.seda_appraisal_rule_duration_value):
            rule = entity.appraisal_rule_duration
            duration = rule.seda_appraisal_rule_duration_value[0].view('saem.concept.alt')
        else:
            duration = _('<no value>')
        self.w('<div><span>%s</span> %s</div>' % (_('seda_appraisal_rule_duration'), duration))
        if (entity.seda_appraisal_rule_code and
                entity.appraisal_rule_code.seda_appraisal_rule_code_value):
            rule = entity.appraisal_rule_code
            code = rule.seda_appraisal_rule_code_value[0].view('oneline')
        else:
            code = xml_escape(_('<no value>'))
        self.w('<div><span>%s</span> %s</div>' % (_('seda_appraisal_rule_code'), code))


class ContentDescriptionValueView(EntityView):
    __regid__ = 'saem.seda.content-description-value'

    def entity_call(self, entity):
        _ = self._cw._
        html = u''
        if entity.seda_description_level[0].seda_description_level_value:
            level = entity.seda_description_level[0].seda_description_level_value[0].view('oneline')
            html += '<div><span>%s</span> %s</div>' % (_('seda_description_level'), level)
        for field in ('description', 'oldest_date', 'latest_date'):
            value_entity = getattr(entity, 'seda_' + field)
            if value_entity:
                value_entity = value_entity[0]
                value = (value_entity.printable_value('value')
                         if value_entity.value else _('<no value>'))
                html += '<div><span>%s</span> %s</div>' % (self._cw.__('seda_' + field),
                                                           xml_escape(value))
        if entity.keywords:
            keywords = self._cw.view('csv', entity.related('seda_keyword_of', 'object'))
            html += '<div><span>%s</span> %s</div>' % (_('seda_keyword_of_object'), keywords)
        self.w(html or xml_escape(_(u'<no value>')))


# forms configuration ##############################################################################


def rtype_concept_label_choices(form, field, label_kind=u'preferred_label'):
    """To be used as a ``choices`` function for an attribute whose objects are SKOS concepts.

    With this function, a combo box will be displayed with a list of labels for all relevant
    concepts. Kind of displayed labels is given by the `label_kind` parameter; by default, preferred
    labels are displayed.
    """
    assert field.name.endswith('_value')
    rtype_name = unicode(field.name[:-6])
    rql = ('Any LABEL,C WHERE S scheme_relation RT, C in_scheme S, C {0} L,'
           ' L label LABEL, RT name %(rtype_name)s').format(label_kind)
    # XXX: if a concept has multiple labels of given kind, they will all appear in the list.
    # This should not happen since these concepts are created programmatically, but a user may edit
    rset = form._cw.execute(rql, {'rtype_name': rtype_name})
    return [(label, unicode(concept_eid)) for label, concept_eid in rset.rows]

rtype_concept_alt_label_choices = partial(rtype_concept_label_choices,
                                          label_kind=u'alternative_label')
rtype_concept_pref_label_choices = partial(rtype_concept_label_choices,
                                           label_kind=u'preferred_label')


afs = uicfg.autoform_section
affk = uicfg.autoform_field_kwargs
aff = uicfg.autoform_field

# name (for archive and archive object)
afs.tag_subject_of(('*', 'seda_name', '*'), 'main', 'inlined')
affk.set_field_kwargs('SEDAName', 'value', widget=fw.TextInput({'size': 80}))

# description (for document and content description)
afs.tag_subject_of(('*', 'seda_description', '*'), 'main', 'inlined')

# content description (for archive and archive object)
afs.tag_subject_of(('*', 'seda_content_description', '*'), 'inlined', 'hidden')
afs.tag_subject_of(('*', 'seda_content_description', '*'), 'main', 'inlined')
afs.tag_object_of(('*', 'seda_keyword_of', '*'), 'main', 'inlined')
afs.tag_subject_of(('*', 'seda_description_level', '*'), 'main', 'inlined')
afs.tag_subject_of(('*', 'seda_oldest_date', '*'), 'main', 'inlined')
afs.tag_subject_of(('*', 'seda_latest_date', '*'), 'main', 'inlined')
afs.tag_subject_of(('SEDAContentDescription', 'seda_description', '*'), 'main', 'inlined')
afs.tag_object_of(('*', 'seda_keyword_of', 'SEDAContentDescription'),
                  'main', 'inlined')
afs.tag_subject_of(('SEDAContentDescription', 'seda_description_level', '*'),
                   'main', 'inlined')
afs.tag_subject_of(('SEDADescriptionLevel', 'seda_description_level_value', '*'),
                   'main', 'attributes')
afs.tag_subject_of(('SEDAContentDescription', 'seda_oldest_date', '*'),
                   'main', 'inlined')
afs.tag_subject_of(('SEDAContentDescription', 'seda_latest_date', '*'),
                   'main', 'inlined')
afs.tag_subject_of(('SEDAKeyword', 'seda_keyword_scheme', '*'),
                   'main', 'attributes')
afs.tag_subject_of(('SEDAKeyword', 'seda_keyword_value', '*'),
                   'main', 'attributes')

affk.set_field_kwargs('SEDAKeyword', 'seda_keyword_value',
                      widget=ConceptAutoCompleteWidget(slave_name='keyword_value',
                                                       master_name='keyword_scheme'))

# appraisal rule (for archive and archive object)
afs.tag_subject_of(('*', 'seda_appraisal_rule', '*'), 'inlined', 'hidden')
afs.tag_subject_of(('*', 'seda_appraisal_rule', '*'), 'main', 'inlined')
afs.tag_subject_of(('SEDAAppraisalRule', 'seda_appraisal_rule_code', '*'),
                   'main', 'inlined')
afs.tag_subject_of(('SEDAAppraisalRule', 'seda_appraisal_rule_duration', '*'),
                   'main', 'inlined')
afs.tag_subject_of(('SEDAAppraisalRuleCode', 'seda_appraisal_rule_code_value', '*'),
                   'main', 'attributes')
afs.tag_subject_of(('SEDAAppraisalRuleDuration', 'seda_appraisal_rule_duration_value', '*'),
                   'main', 'attributes')
affk.tag_subject_of(('SEDAAppraisalRuleDuration', 'seda_appraisal_rule_duration_value', '*'),
                    {'choices': rtype_concept_alt_label_choices})

# simple link-to-concept attributes (for archive, archive object and document)
for attr in ('seda_access_restriction_code',
             'seda_document_type_code', 'seda_file_type_code', 'seda_character_set_code'):
    afs.tag_subject_of(('*', attr, '*'), 'inlined', 'hidden')
    afs.tag_subject_of(('*', attr, '*'), 'main', 'inlined')
    afs.tag_subject_of(('*', attr + '_value', '*'), 'main', 'attributes')
    if attr == 'seda_access_restriction_code':  # Use a relation widget for access restriction code
        affk.tag_subject_of(('*', attr + '_value', '*'),
                            {'widget': rwdg.RelationFacetWidget(dialog_options={'width': 800})})
    elif attr == 'seda_document_type_code':  # Use a combo box for each other rtype
        affk.tag_subject_of(('*', attr + '_value', '*'),
                            {'choices': rtype_concept_pref_label_choices})
    else:
        affk.tag_subject_of(('*', attr + '_value', '*'),
                            {'choices': rtype_concept_alt_label_choices})

# children (for archive and archive object)
afs.tag_object_of(('*', 'seda_parent', '*'), 'main', 'hidden')
afs.tag_subject_of(('*', 'seda_parent', '*'), 'main', 'hidden')

# metadata attributes
aff.tag_attribute(('*', 'user_annotation'), SEDAMetaField)
afs.tag_attribute(('*', 'user_cardinality'), 'main', 'hidden')  # handled by SEDAMetaField

# clone relation
afs.tag_subject_of(('*', 'seda_clone_of', '*'), 'main', 'hidden')
afs.tag_object_of(('*', 'seda_clone_of', '*'), 'main', 'hidden')
afs.tag_subject_of(('*', 'seda_replace', '*'), 'main', 'hidden')
afs.tag_object_of(('*', 'seda_replace', '*'), 'main', 'hidden')


class SEDAMetaStringField(SEDAMetaFieldMixIn, ff.StringField):
    pass


aff.tag_attribute(('SEDAName', 'value'), SEDAMetaStringField)
afs.tag_attribute(('SEDAName', 'user_annotation'), 'main', 'hidden')
aff.tag_attribute(('SEDADescription', 'value'), SEDAMetaStringField)
afs.tag_attribute(('SEDADescription', 'user_annotation'), 'main', 'hidden')
aff.tag_attribute(('SEDAAppraisalRuleDuration', 'value'), SEDAMetaStringField)
afs.tag_attribute(('SEDAAppraisalRuleDuration', 'user_annotation'), 'main', 'hidden')


class SEDAMetaDateField(SEDAMetaFieldMixIn, ff.DateField):
    pass

aff.tag_attribute(('SEDADate', 'value'), SEDAMetaDateField)
afs.tag_attribute(('SEDADate', 'user_annotation'), 'main', 'hidden')


class SEDAMetaRelationField(SEDAMetaFieldMixIn, ff.RelationField):
    pass

aff.tag_attribute(('SEDADescriptionLevel', 'seda_description_level_value'),
                  SEDAMetaRelationField)
afs.tag_attribute(('SEDADescriptionLevel', 'user_annotation'), 'main', 'hidden')
aff.tag_attribute(('SEDAAppraisalRuleCode', 'seda_appraisal_rule_code_value'),
                  SEDAMetaRelationField)
afs.tag_attribute(('SEDAAppraisalRuleCode', 'user_annotation'), 'main', 'hidden')
aff.tag_attribute(('SEDAAccessRestrictionCode', 'seda_access_restriction_code_value'),
                  SEDAMetaRelationField)
afs.tag_attribute(('SEDAAccessRestrictionCode', 'user_annotation'), 'main', 'hidden')

aff.tag_attribute(('SEDAFileTypeCode', 'seda_file_type_code_value'), SEDAMetaRelationField)
afs.tag_attribute(('SEDAFileTypeCode', 'user_annotation'), 'main', 'hidden')
aff.tag_attribute(('SEDADocumentTypeCode', 'seda_document_type_code_value'), SEDAMetaRelationField)
afs.tag_attribute(('SEDADocumentTypeCode', 'user_annotation'), 'main', 'hidden')
aff.tag_attribute(('SEDACharacterSetCode', 'seda_character_set_code_value'), SEDAMetaRelationField)
afs.tag_attribute(('SEDACharacterSetCode', 'user_annotation'), 'main', 'hidden')

# hide parent objects
afs.tag_object_of(('*', 'seda_content_description', '*'), 'main', 'hidden')
afs.tag_object_of(('*', 'seda_appraisal_rule', '*'), 'main', 'hidden')
afs.tag_subject_of(('*', 'seda_keyword_of', '*'), 'main', 'hidden')
afs.tag_subject_of(('*', 'seda_parent', '*'), 'main', 'hidden')
pvs.tag_object_of(('*', 'seda_content_description', '*'), 'hidden')
pvs.tag_object_of(('*', 'seda_appraisal_rule', '*'), 'hidden')
pvs.tag_subject_of(('*', 'seda_keyword_of', '*'), 'hidden')
pvs.tag_subject_of(('*', 'seda_parent', '*'), 'hidden')
for rtype in ('seda_access_restriction_code', 'seda_document_type_code', 'seda_file_type_code',
              'seda_character_set_code'):
    afs.tag_object_of(('*', rtype, '*'), 'main', 'hidden')
    afs.tag_object_of(('*', rtype + '_value', '*'), 'main', 'hidden')
    pvs.tag_object_of(('*', rtype, '*'), 'hidden')
    pvs.tag_object_of(('*', rtype + '_value', '*'), 'hidden')

# finalize SEDAProfile form
affk.set_field_kwargs('SEDAProfile', 'ark', widget=fw.TextInput({'size': 80}), required=False)
affk.set_field_kwargs('SEDAProfile', 'title', widget=fw.TextInput({'size': 80}))


# shared configuration #############################################################################

affk.set_fields_order('SEDAContentDescription', ('user_cardinality', 'user_annotation',
                                                 'seda_description_level',
                                                 'seda_oldest_date', 'seda_latest_date',
                                                 'seda_keyword_of'))
pvds.set_fields_order('SEDAContentDescription', ('user_cardinality', 'user_annotation',
                                                 'seda_description_level', 'seda_description',
                                                 'seda_oldest_date', 'seda_latest_date',
                                                 'seda_keyword_of'))
affk.set_fields_order('SEDADescriptionLevel', ('seda_description_level_value', 'user_annotation'))
pvds.set_fields_order('SEDADescriptionLevel', ('seda_description_level_value', 'user_annotation'))
affk.set_fields_order('SEDAKeyword', ('user_cardinality', 'user_annotation',
                                      'seda_keyword_scheme', 'seda_keyword_value', ))
pvds.set_fields_order('SEDAKeyword', ('user_cardinality', 'user_annotation',
                                      'seda_keyword_scheme', 'seda_keyword_value', ))
affk.set_fields_order('SEDAAccessRestrictionCode', ('seda_access_restriction_code_value',
                                                    'user_cardinality', 'user_annotation'))
pvds.set_fields_order('SEDAAccessRestrictionCode', ('seda_access_restriction_code_value',
                                                    'user_cardinality', 'user_annotation'))
affk.set_fields_order('SEDAAppraisalRuleCode', ('seda_appraisal_rule_code_value',
                                                'user_annotation'))
pvds.set_fields_order('SEDAAppraisalRuleCode', ('seda_appraisal_rule_code_value',
                                                'user_annotation'))
affk.set_fields_order('ProfileArchiveObject', ('user_cardinality', 'user_annotation', 'seda_name'))
pvds.set_fields_order('ProfileArchiveObject', ('user_cardinality', 'user_annotation', 'seda_name'))

affk.set_fields_order('ProfileDocument', (
    'user_cardinality', 'user_annotation', 'seda_document_type_code', 'seda_description',
    'seda_character_set_code', 'seda_file_type_code'))
pvds.set_fields_order('ProfileDocument', (
    'user_cardinality', 'user_annotation', 'seda_document_type_code', 'seda_description',
    'seda_character_set_code', 'seda_file_type_code'))

affk.set_fields_order('SEDADocumentTypeCode',
                      ('seda_document_type_code_value', 'user_cardinality', 'user_annotation'))
pvds.set_fields_order('SEDADocumentTypeCode',
                      ('seda_document_type_code_value', 'user_cardinality', 'user_annotation'))
affk.set_fields_order('SEDAFileTypeCode',
                      ('seda_file_type_code_value', 'user_cardinality', 'user_annotation'))
pvds.set_fields_order('SEDAFileTypeCode',
                      ('seda_file_type_code_value', 'user_cardinality', 'user_annotation'))
affk.set_fields_order('SEDACharacterSetCode',
                      ('seda_character_set_code_value', 'user_cardinality', 'user_annotation'))
pvds.set_fields_order('SEDACharacterSetCode',
                      ('seda_character_set_code_value', 'user_cardinality', 'user_annotation'))


# views ############################################################################################

class NoLinkOneLineView(baseviews.OneLineView):
    __select__ = is_instance('SEDAName', 'SEDADescription', 'SEDADate', 'SEDAKeyword')

    def cell_call(self, row, col, **kwargs):
        """one line view without link to the entity """
        entity = self.cw_rset.get_entity(row, col)
        self.w(entity.dc_title())


class NoLinkInContextView(NoLinkOneLineView):
    __regid__ = 'incontext'


class NoLinkOutOfContextView(NoLinkOneLineView):
    __regid__ = 'outofcontext'


class ConceptAltLabelView(EntityView):
    __regid__ = 'saem.concept.alt'
    __select__ = is_instance('Concept')

    def entity_call(self, entity):
        desc = entity.preferred_label[0].label
        title = (entity.alternative_label[0].label
                 if entity.alternative_label else entity.dc_title())
        self.w(u'<a href="%s" title="%s">%s</a>' % (
            xml_escape(entity.absolute_url()), xml_escape(desc),
            xml_escape(title)))


# navigation #######################################################################################

class SEDAComponentsBreadcrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    """Breadcrumbs adapter pointing to /sedalib route when entity has no
    parent.
    """
    __select__ = (ibreadcrumbs.IBreadCrumbsAdapter.__select__
                  & relation_possible('seda_parent', role='subject')
                  & ~has_related_entities('seda_parent', role='subject'))

    def breadcrumbs(self, *args, **kwargs):
        return [(self._cw.build_url('sedalib'), self._cw._('SEDA components')),
                self.entity]


# hack autoform_section rtags using the draft 'selectable' rtags feature ###########################

def related_to_profile_archive(entity):
    """Return `1` if given `SEDAAccessRestrictionCode` entity is related through the
    `seda_access_restriction_code` relation to a `ProfileArchive`, else `0`.
    """
    if entity.has_eid():
        parent = entity.reverse_seda_access_restriction_code[0]
    else:
        # use .get since when related to a ProfileArchiveObject, the SEDAAccessRestrictionCode may
        # be acccessed through ajax hence missing the 'etype' key in form params
        # related_etype = entity._cw.form.get('etype')
        return 0  # XXX attempt to retrieve parent
    return int(parent.first_level)

paac_afs = deepcopy(afs)
paac_afs.__module__ = __name__
paac_afs.__select__ = (is_instance('SEDAAccessRestrictionCode')
                       & score_entity(related_to_profile_archive))
paac_afs.tag_attribute(('SEDAAccessRestrictionCode', 'user_cardinality'), 'main', 'hidden')


# custom form renderers ############################################################################

class SEDAValueEntityInlinedFormRenderer(formrenderers.EntityInlinedFormRenderer):
    __select__ = formrenderers.EntityInlinedFormRenderer.__select__ & is_instance(
        'SEDAAppraisalRuleDuration', 'SEDAAppraisalRuleCode',
        'SEDAAccessRestrictionCode', 'SEDADescriptionLevel',
        'SEDAFileTypeCode', 'SEDACharacterSetCode', 'SEDADocumentTypeCode',
        'SEDAName', 'SEDADescription', 'SEDADate')

    def render_title(self, w, form, values):
        """Overriden from :class:`formrenderers.EntityInlinedFormRenderer` to skip the title"""
        if values['removejs']:
            w(u'<div class="iformTitle">')
            values['removemsg'] = self._cw._('remove-inlined-entity-form')
            w(u'[<a href="javascript: %(removejs)s;$.noop();">%(removemsg)s</a>]'
              % values)
            w(u'</div>')

    def render_label(self, form, field):
        """Overriden from :class:`formrenderers.EntityInlinedFormRenderer` to set the label
        according to the relation to the parent entity.
        """
        if field.name.endswith('value'):
            # XXX rely on 'id' to search for the field holding the relation to the parent entity
            field = [f for f in form.fields if f.id and f.id.startswith('rel-')][0]
        return super(SEDAValueEntityInlinedFormRenderer, self).render_label(form, field)


class SEDACompoundEntityInlinedFormRenderer(formrenderers.EntityInlinedFormRenderer):
    __select__ = formrenderers.EntityInlinedFormRenderer.__select__ & is_instance(
        'SEDAContentDescription', 'SEDAAppraisalRule', 'SEDAKeyword')

    def open_form(self, w, form, values):
        """Overriden from :class:`formrenderers.EntityInlinedFormRenderer` to add the 'formGroup'
        class to then enclosing div. Beside this, HTML structure is left unchanged and so opened
        div are closed in :meth:`formrenderers.EntityInlinedFormRenderer.close_form`
        """
        try:
            w(u'<div id="div-%(divid)s" onclick="%(divonclick)s" class="formGroup">' % values)
        except KeyError:
            w(u'<div id="div-%(divid)s" class="formGroup">' % values)
        else:
            w(u'<div id="notice-%s" class="notice">%s</div>' % (
                values['divid'], self._cw._('click on the box to cancel the deletion')))
        w(u'<div class="iformBody">')


# customization of relation widget for concepts ####################################################

class SearchForRelatedConceptsView(rwdg.SearchForRelatedEntitiesView):
    __abstract__ = True
    rtype = None
    has_creation_form = False

    def linkable_rset(self):
        """Return rset of entities to be displayed as possible values for the edited relation."""
        # XXX can't use alternative_label computed relation until
        # https://www.cubicweb.org/ticket/5497433 is fixed
        rql = ('Any C,CPL,CPLL,CAL,CALL,CD ORDERBY CPLL WHERE '
               'C in_scheme S, S scheme_relation RT, RT name %(rtype)s, '
               'C preferred_label CPL, CPL label CPLL, CAL? label_of C, CAL kind "alternative", '
               'CAL label CALL, C definition CD')
        return self._cw.execute(rql, {'rtype': self.rtype})

    @staticmethod
    def pref_label_label(concept):
        return concept.cw_rset.get_entity(concept.cw_row, 1).label

    @staticmethod
    def pref_label_column(w, concept):
        w(tags.a(SearchForRelatedConceptsView.pref_label_label(concept),
                 href=concept.absolute_url()))

    @staticmethod
    def alt_label(concept):
        if concept.cw_rset[concept.cw_row][3] is not None:
            return concept.cw_rset.get_entity(concept.cw_row, 3)
        return None


class SearchForAccessRestrictionConceptsView(SearchForRelatedConceptsView):
    rtype = 'seda_access_restriction_code'
    __select__ = SearchForRelatedConceptsView.__select__ & rwdg.edited_relation(rtype + '_value')


class SearchForDescriptionLevelConceptsView(SearchForRelatedConceptsView):
    rtype = 'seda_description_level'
    __select__ = SearchForRelatedConceptsView.__select__ & rwdg.edited_relation(rtype + '_value')


class SelectConceptEntitiesTableView(rwdg.SelectEntitiesTableView):
    """Table view of the selectable entities in the relation widget

    Selection of columns (and respective renderer) can be overridden by
    updating `columns` and `column_renderers` class attributes.
    """
    __select__ = (rwdg.SelectEntitiesTableView.__select__
                  & is_instance('Concept')
                  & rwdg.edited_relation([rtype + '_value' for rtype in (
                      'seda_access_restriction_code', 'seda_description_level')]))

    columns = rwdg.SelectEntitiesTableView.columns + ['alternative_label', 'definition']
    column_renderers = rwdg.SelectEntitiesTableView.column_renderers.copy()
    # speed-up things by considering rset shape from SearchForRelatedConceptsView
    column_renderers['entity'] = rwdg.SelectMainEntityColRenderer(
        sortfunc=SearchForRelatedConceptsView.pref_label_label,
        renderfunc=SearchForRelatedConceptsView.pref_label_column)
    column_renderers['alternative_label'] = tableview.RelatedEntityColRenderer(
        getrelated=SearchForRelatedConceptsView.alt_label)


# tree box #########################################################################################

class SEDAProfileTreeBox(component.EntityCtxComponent):
    """display a box containing the whole SEDA profile tree"""
    __regid__ = 'saem.seda.tree'
    __select__ = is_instance('SEDAProfile')
    title = _('SEDA profile objects tree')
    order = 10

    def render_body(self, w):
        self.entity.view('jqtree.treeview', w=w)


class ProfileArchiveObjectTreeBox(SEDAProfileTreeBox):
    __select__ = is_instance('ProfileArchiveObject')
    title = _('Profile archive object objects tree')


class SEDAJsonTreeView(jqtree.JsonTreeView):
    __select__ = jqtree.JsonTreeView.__select__ & is_instance(
        'SEDAProfile', 'ProfileArchiveObject', 'ProfileDocument')

    def entity_call(self, entity, **kwargs):
        root = entity.cw_adapt_to('ITree').root()
        if root.cw_etype == 'SEDAProfile' and not root.support_seda_exports:
            errors = defaultdict(list)
            for eid, msg in root.cw_adapt_to('SEDA-0.2.xsd').blockers():
                errors[eid].append(self._cw._(msg))
            self._cw.data['seda-export-errors'] = errors
        super(SEDAJsonTreeView, self).entity_call(entity, **kwargs)


class JQTreeErrorItemLabelView(jqtree.JQTreeItemLabelView):
    """Override default label view in case the entity has some seda export error."""
    __select__ = (jqtree.JQTreeItemLabelView.__select__
                  & score_entity(lambda x: x.eid in x._cw.data.get('seda-export-errors', ())))

    def entity_call(self, entity):
        super(JQTreeErrorItemLabelView, self).entity_call(entity)
        title = '\n'.join(self._cw.data['seda-export-errors'][entity.eid])
        self.w(tags.span(u'', title=title, klass='seda-export-error icon-attention'))


@ajaxcontroller.ajaxfunc(output_type='json')
def seda_movable(self, eid):
    """Return True if entity with `eid` may be moved in a SEDAProfile tree.
    """
    etype = self._cw.describe(eid)[0]
    schema = self._cw.vreg.schema
    eschema = schema[etype]
    return 'seda_parent' in eschema.subjrels


@ajaxcontroller.ajaxfunc(output_type='json')
def seda_may_set_parent(self, fromeid, toeid):
    """Return True if a `seda_parent` relation maybe be added between entities
    with `fromeid` and `toeid` eids.
    """
    frometype = self._cw.describe(fromeid)[0]
    toetype = self._cw.describe(toeid)[0]
    schema = self._cw.vreg.schema
    try:
        rdef = schema['seda_parent'].rdef(frometype, toetype)
    except KeyError:
        # No seda_parent relation between requested entity types.
        return False
    try:
        rdef.check_perm(self._cw, 'add', toeid=toeid, fromeid=fromeid)
    except Unauthorized:
        return False
    return True


@ajaxcontroller.ajaxfunc(output_type='json')
def seda_reparent(self, child_eid, parent_eid):
    """Add a `seda_parent` relation between two entities.
    """
    self._cw.execute(
        'SET C seda_parent P WHERE C eid %(c)s, P eid %(p)s',
        {'c': child_eid, 'p': parent_eid})


# life-cycle management ############################################################################

# Hide copy action for SEDA profiles
actions.CopyAction.__select__ = actions.CopyAction.__select__ & ~is_instance('SEDAProfile')


# Only show clone action for SEDA profiles if no clone has been created yet

class SEDAProfileCloneAction(CloneAction):
    __select__ = (CloneAction.__select__
                  & is_instance('SEDAProfile')
                  & ~has_related_entities('seda_replace', 'object')
                  & is_in_state('published'))
    title = _('new version')
    category = 'mainactions'

CloneAction.__select__ &= ~is_instance('SEDAProfile')


class NoWarningCopyFormView(editforms.CopyFormView):
    """display primary entity creation form initialized with values from another
    entity
    """
    __select__ = editforms.CopyFormView.__select__ & is_instance('SEDAProfile')

    def render_form(self, entity):
        """fetch and render the form"""
        # make a copy of entity to avoid altering the entity in the
        # request's cache.
        entity.complete()
        self.newentity = copy(entity)
        self.copying = entity
        self.newentity.eid = self._cw.varmaker.next()
        super(editforms.CopyFormView, self).render_form(self.newentity)
        del self.newentity


def workflow_state(entity):
    """Return the state of the given entity."""
    return entity.cw_adapt_to('IWorkflowable').state


class SEDAProfileRelatedVersionsComponent(component.EntityCtxComponent):
    """Output a box containing relevant SEDA Profiles related to the current one."""
    __regid__ = 'saem.seda.relatedprofiles'
    __select__ = (component.EntityCtxComponent.__select__ &
                  (has_related_entities('seda_replace', role='subject') |
                   has_related_entities('seda_replace', role='object')))
    context = 'incontext'
    order = 11
    title = _('Related versions')

    def predecessor(self):
        """Yield the profile of which the displayed profile is a new version (draft or published).
        """
        if (workflow_state(self.entity) in (u'published', u'draft') and
                self.entity.predecessor):
            yield self.entity.predecessor

    def current_version(self, state):
        """Yield the latest profile, either published or draft, that replaces the displayed one.

        ``state`` parameter must be either "draft" or "published".
        """
        assert state in (u'published', u'draft')
        successor = self.entity.successor
        while successor and workflow_state(successor) != state:
            successor = successor.successor
        if successor:
            yield successor

    def render_body(self, w):
        profile_state = workflow_state(self.entity)
        display_entities = []
        if profile_state == u'draft':
            display_entities += self.predecessor()
        elif profile_state == u'published':
            display_entities += self.current_version(u'draft')
            display_entities += self.predecessor()
        elif profile_state == u'deprecated':
            display_entities += self.current_version(u'published')
        if display_entities:
            w(u'<ul class="list-group">')
            for entity in display_entities:
                w(u'<li class="list-group-item">')
                w(tags.span(self._cw._(workflow_state(entity)), klass='badge'))
                entity.view('incontext', w=w)
                w(u'</li>')
            w(u'</ul>')


# SEDA import ######################################################################################

def _import_div_id(entity):
    return 'importDiv%s' % entity.eid


class SEDAPrimaryView(primary.PrimaryView):
    """Overriden to add an extra empty div that may be used to insert import's relation widget"""
    __select__ = (primary.PrimaryView.__select__
                  & is_instance('SEDAProfile', 'ProfileArchiveObject')
                  & has_permission('update'))

    def entity_call(self, entity, **kwargs):
        super(SEDAPrimaryView, self).entity_call(entity, **kwargs)
        rwdg.boostrap_dialog(self.w, self._cw._, _import_div_id(entity), u'')


class SEDAImportAction(action.Action):
    __abstract__ = True

    __select__ = (action.Action.__select__
                  & one_line_rset()
                  & has_permission('update'))

    category = 'moreactions'
    submenu = _('import menu')
    etype = None  # to be specified in concrete classes

    @property
    def title(self):
        return self._cw._(self.etype).lower()

    def fill_menu(self, box, menu):
        # when there is only one item in the sub-menu, replace the sub-menu by
        # item's title prefixed by 'add'
        menu.label_prefix = self._cw._('import menu')
        super(SEDAImportAction, self).fill_menu(box, menu)

    def url(self):
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        root = entity.cw_adapt_to('ITree').root()
        relation = 'seda_clone_of:%s:subject' % self.etype
        search_url = self._cw.build_url('ajax', fname='view', vid='search_related_entities',
                                        __modal=1, multiple='', relation=relation,
                                        etype=root.cw_etype, target=root.eid)
        title = self._cw._('Search entity to import')
        return configure_relation_widget(self._cw, _import_div_id(entity), search_url, title,
                                         False, uilib.js.saem.buildSedaImportValidate(entity.eid))


class SEDAImportProfileArchiveObjectAction(SEDAImportAction):
    __regid__ = 'saem_ref.seda.import.documentunit'
    __select__ = SEDAImportAction.__select__ & is_instance('SEDAProfile', 'ProfileArchiveObject')
    etype = 'ProfileArchiveObject'


class SEDAImportProfileDocumentAction(SEDAImportAction):
    __regid__ = 'saem_ref.seda.import.attachment'
    __select__ = SEDAImportAction.__select__ & is_instance('ProfileArchiveObject')
    etype = 'ProfileDocument'


class SEDADoImportView(controller.Controller):
    __regid__ = 'saem_ref.seda.doimport'
    __select__ = match_form_params('eid', 'cloned')

    def publish(self, rset=None):
        parent = self._cw.entity_from_eid(int(self._cw.form['eid']))
        original = self._cw.entity_from_eid(int(self._cw.form['cloned']))
        clone = copy_entity(original, seda_parent=parent, seda_clone_of=original)
        msg = self._cw._('{0} has been imported').format(clone.dc_title())
        raise Redirect(parent.absolute_url(__message=msg))


class SearchForDocumentUnitToImportView(rwdg.SearchForRelatedEntitiesView):
    __select__ = (SearchForRelatedConceptsView.__select__
                  & rwdg.edited_relation('seda_clone_of')
                  & match_form_params('target'))
    title = None

    def linkable_rset(self):
        """Return rset of entities to be displayed as possible values for the edited relation."""
        tetype = self._cw.form['relation'].split(':')[1]
        target = int(self._cw.form['target'])
        rql = ('Any X,MD ORDERBY MD DESC WHERE X is %s, X modification_date MD, '
               'NOT X seda_parent P, NOT X eid %%(target)s') % tetype
        return self._cw.execute(rql, {'target': target})


class SelectProfileDocumentEntitiesTableView(rwdg.SelectEntitiesTableView):
    """Table view for ProfileDocument entities in a relation widget."""

    __select__ = (rwdg.SelectEntitiesTableView.__select__
                  & is_instance('ProfileDocument')
                  & rwdg.edited_relation('seda_clone_of'))

    columns = rwdg.SelectEntitiesTableView.columns + ['seda_description', 'seda_file_type_code']
    column_renderers = rwdg.SelectEntitiesTableView.column_renderers.copy()
    column_renderers['seda_description'] = tableview.RelatedEntityColRenderer(
        getrelated=lambda x: x.description)
    column_renderers['seda_file_type_code'] = tableview.RelatedEntityColRenderer(
        getrelated=lambda x: x.file_type_code, vid='saem.seda.concept-value')


class SelectProfileArchiveObjectEntitiesTableView(rwdg.SelectEntitiesTableView):
    """Table view ProfileArchiveObject entities in the relation widget."""

    __select__ = (rwdg.SelectEntitiesTableView.__select__
                  & is_instance('ProfileArchiveObject')
                  & rwdg.edited_relation('seda_clone_of'))

    columns = rwdg.SelectEntitiesTableView.columns[:]
    columns += ['seda_content_description', 'seda_description_level',
                'seda_appraisal_rule']
    column_renderers = rwdg.SelectEntitiesTableView.column_renderers.copy()
    column_renderers['entity'] = rwdg.SelectMainEntityColRenderer(vid='saem.seda.du.name')
    column_renderers['seda_name'] = tableview.RelatedEntityColRenderer(
        getrelated=lambda x: x.seda_name[0])
    column_renderers['seda_content_description'] = tableview.RelatedEntityColRenderer(
        getrelated=lambda x: x.content_description and x.content_description.description)
    column_renderers['seda_description_level'] = tableview.RelatedEntityColRenderer(
        getrelated=lambda x: x.content_description and x.content_description.description_level,
        vid='saem.seda.concept-value')
    column_renderers['seda_appraisal_rule'] = tableview.RelatedEntityColRenderer(
        getrelated=lambda x: x.appraisal_rule and x.appraisal_rule.appraisal_rule_code,
        vid='saem.seda.concept-value')


class DocumentUnitNameView(EntityView):
    __regid__ = 'saem.seda.du.name'
    __select__ = is_instance('ProfileArchiveObject')

    def entity_call(self, entity):
        self.w(tags.a(entity.name.dc_title(), href=entity.absolute_url(), target='_blank'))


class ConceptValueView(EntityView):
    """Display related concept if any, else attempt to fallback to user annotation."""
    __abstract__ = True
    __regid__ = 'saem.seda.concept-value'
    concept_rtype = None
    label_rtype = 'preferred_label'

    def label(self, entity):
        concepts = getattr(entity, self.concept_rtype)
        if concepts:
            return getattr(concepts[0], self.label_rtype)[0].printable_value('label')
        return None

    def entity_call(self, entity):
        label = self.label(entity)
        if label is None:
            label = entity.printable_value('user_annotation')
        if label:
            self.w(label)


class SEDAAppraisalRuleCodeConceptValueView(ConceptValueView):
    __select__ = is_instance('SEDAAppraisalRuleCode')
    concept_rtype = 'seda_appraisal_rule_code_value'


class SEDADescriptionLevelConceptValueView(ConceptValueView):
    __select__ = is_instance('SEDADescriptionLevel')
    concept_rtype = 'seda_description_level_value'


class SEDAFileTypeCodeConceptValueView(ConceptValueView):
    __select__ = is_instance('SEDAFileTypeCode')
    concept_rtype = 'seda_file_type_code_value'
    label_rtype = 'alternative_label'


# SEDA download ####################################################################################

class SEDA1DownloadAction(action.Action):
    __regid__ = 'saem_ref.seda1'
    __select__ = (action.Action.__select__
                  & one_line_rset()
                  & is_instance('SEDAProfile')
                  & score_entity(lambda x: 'SEDA-1.0.xsd' in x.support_seda_exports))

    title = _('SEDA 1.0 export')
    category = 'moreactions'
    seda_download_vid = 'saem_ref.seda1'

    def url(self):
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        return entity.absolute_url(vid=self.seda_download_vid)


class SEDA1DownloadView(idownloadable.DownloadView):
    """SEDA 1.0 download view"""
    __regid__ = 'saem_ref.seda1'
    __select__ = one_line_rset() & is_instance('SEDAProfile')

    http_cache_manager = httpcache.NoHTTPCacheManager
    seda_adapter_id = 'SEDA-1.0.xsd'

    def set_request_content_type(self):
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        adapter = entity.cw_adapt_to(self.seda_adapter_id)
        self._cw.set_content_type(adapter.content_type, filename=adapter.file_name,
                                  encoding=adapter.encoding, disposition='attachment')

    def call(self):
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        adapter = entity.cw_adapt_to(self.seda_adapter_id)
        self.w(adapter.dump())


class SEDA02DownloadAction(SEDA1DownloadAction):
    __regid__ = 'saem_ref.seda02'
    __select__ = (action.Action.__select__
                  & one_line_rset()
                  & is_instance('SEDAProfile')
                  & score_entity(lambda x: 'SEDA-0.2.xsd' in x.support_seda_exports))
    title = _('SEDA 0.2 export')
    seda_download_vid = 'saem_ref.seda02'


class SEDA02DownloadView(SEDA1DownloadView):
    """SEDA 0.2 download view"""
    __regid__ = 'saem_ref.seda02'
    seda_adapter_id = 'SEDA-0.2.xsd'


# SEDA lib components ##############################################################################


class AddEntityComponent(component.CtxComponent):
    """Component with 'add' link to be displayed in 'same etype' views usually 'SameETypeListView'.
    """
    __regid__ = 'saem_ref.add_entity'
    __select__ = (component.CtxComponent.__select__
                  & multi_lines_rset()
                  & has_permission('add')
                  & is_instance('ProfileArchiveObject', 'ProfileDocument')
                  & score_entity(lambda x: not x.seda_parent))
    context = 'navtop'

    def render_body(self, w):
        req = self._cw
        links = [add_etype_link(req, etype, req._(etype), klass='')
                 for etype in ('ProfileArchiveObject', 'ProfileDocument')]
        w(index_dropdown_button(req._('Add a new component'), links))


class SEDALibView(baseviews.SameETypeListView):
    __regid__ = 'saem_ref.sedalib'
    __select__ = (multi_lines_rset()
                  & is_instance('ProfileArchiveObject', 'ProfileDocument')
                  & score_entity(lambda x: not x.seda_parent))

    @property
    def title(self):
        return self._cw._('SEDA components')
