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
"""cubicweb-saem-ref views for AuthorityRecord"""

from functools import partial

from logilab.common.date import ustrftime
from logilab.mtconverter import xml_escape

from cubicweb import tags
from cubicweb.utils import json_dumps, make_uid, JSString
from cubicweb.uilib import cut, js
from cubicweb.view import EntityView
from cubicweb.predicates import (adaptable, has_related_entities, is_instance, match_kwargs,
                                 score_entity)
from cubicweb.web import component, formfields as ff, formwidgets as fw
from cubicweb.web.views import calendar, tabs, uicfg, actions

from cubes.saem_ref import cwuri_url, user_has_authority
from . import (ImportEntityComponent, RelatedEntitiesListView, SubviewsTabView,
               editlinks, external_link)
from .widgets import JQueryIncompleteDatePicker, ConceptAutoCompleteWidget

_ = unicode

abaa = uicfg.actionbox_appearsin_addmenu
pvs = uicfg.primaryview_section
pvds = uicfg.primaryview_display_ctrl
rdc = uicfg.reledit_ctrl
afs = uicfg.autoform_section
aff = uicfg.autoform_field
affk = uicfg.autoform_field_kwargs


for etype in ('AuthorityRecord',
              'AssociationRelation', 'ChronologicalRelation', 'HierarchicalRelation',
              'Mandate', 'LegalStatus', 'EACResourceRelation'):
    affk.set_field_kwargs(etype, 'start_date',
                          widget=JQueryIncompleteDatePicker(update_min='end_date'))
    affk.set_field_kwargs(etype, 'end_date',
                          widget=JQueryIncompleteDatePicker(update_max='start_date',
                                                            default_end=True))


class EACImportComponent(ImportEntityComponent):
    """Component with a link to import an authority record from an EAC-CPF file."""
    __select__ = (ImportEntityComponent.__select__
                  & is_instance('AuthorityRecord')
                  & user_has_authority())
    _('Import AuthorityRecord')  # generate message used by the import component

    @property
    def import_url(self):
        return self._cw.build_url('view', vid='saem_ref.eac-import')


# Forms
for etype, attr in (
    ('AuthorityRecord', 'isni'),
    ('AuthorityRecord', 'ark'),
    ('AgentPlace', 'name'),
    ('AgentPlace', 'role'),
    ('ConceptScheme', 'ark'),
    ('Concept', 'ark'),
    ('Activity', 'type'),
    ('Mandate', 'term'),
    ('LegalStatus', 'term'),
    ('EACResourceRelation', 'agent_role'),
    ('EACResourceRelation', 'resource_role'),
    ('EACSource', 'title'),
    ('EACSource', 'url'),
):
    affk.set_field_kwargs(etype, attr, widget=fw.TextInput({'size': 80}))
    if attr == 'ark':
        affk.set_field_kwargs(etype, attr, required=False)


# Configure edition of entity types supporting vocabulary_source/equivalent_concept

class EquivalentConceptOrTextField(ff.Field):
    def __init__(self, **kwargs):
        super(EquivalentConceptOrTextField, self).__init__(required=True, **kwargs)
        self.help = _('when linked to a vocabulary, the value is enforced to the label of a '
                      'concept in this vocabulary. Remove the vocabulary source if you want to '
                      'type text freely.')

    def get_widget(self, form):
        return ConceptAutoCompleteWidget(self.name, 'vocabulary_source', optional=True)

    def has_been_modified(self, form):
        return True  # handled in process_posted below

    def process_posted(self, form):
        posted = form._cw.form
        text_val = posted.get(self.input_name(form, 'Label'), '').strip()
        equivalent_eid = posted.get(self.input_name(form), '').strip()
        equivalent_eids = set()
        if equivalent_eid:
            equivalent_eids.add(int(equivalent_eid))
        if not (text_val or equivalent_eid):
            raise ff.ProcessFormError(form._cw.__("required field"))
        entity = form.edited_entity
        if not entity.has_eid() or getattr(entity, self.name) != text_val:
            yield (ff.Field(name=self.name, role='subject', eidparam=True), text_val)
        if (not entity.has_eid() and equivalent_eids) \
           or (entity.has_eid() and
               set(x.eid for x in entity.equivalent_concept) != equivalent_eids):
            subfield = ff.Field(name='equivalent_concept', role='subject', eidparam=True)
            # register the association between the value and the field, because on entity creation,
            # process_posted will be recalled on the newly created field, and if we don't do that it
            # won't find the proper value (this is very nasty)
            form.formvalues[(subfield, form)] = equivalent_eids
            yield (subfield, equivalent_eids)


for etype, attrs in [('AgentFunction', ('name', 'description')),
                     ('AgentPlace', ('name', 'role')),
                     ('Mandate', ('term', 'description')),
                     ('LegalStatus', ('term', 'description')),
                     ('Occupation', ('term', 'description'))]:
    aff.tag_subject_of((etype, attrs[0], '*'), EquivalentConceptOrTextField)
    affk.set_fields_order(etype, ('vocabulary_source',) + attrs)
    if attrs[-1] == 'description':
        affk.tag_attribute((etype, 'description'),
                           {'help': _('let this unspecified to see the definition of the '
                                      'related concept if a vocabulary is specifed')})

afs.tag_object_of(('*', 'vocabulary_source', '*'), 'main', 'hidden')
afs.tag_subject_of(('*', 'vocabulary_source', '*'), 'main', 'attributes')
afs.tag_object_of(('*', 'equivalent_concept', '*'), 'main', 'hidden')
# handled by EquivalentConceptOrTextField
afs.tag_subject_of(('*', 'equivalent_concept', '*'), 'main', 'hidden')
pvs.tag_subject_of(('*', 'equivalent_concept', '*'), 'attributes')
pvs.tag_object_of(('*', 'vocabulary_source', '*'), 'hidden')


# Autocomplete authority record's name

class TextInputCheckSimilar(fw.TextInput):
    """Search for similar authority record names in the database and display them to the user"""

    def __init__(self, *args, **kwargs):
        self.data_initfunc = kwargs.pop('data_initfunc')
        super(TextInputCheckSimilar, self).__init__(*args, **kwargs)

    def _render(self, form, field, render):
        req = form._cw
        req.add_js('cubes.saem_ref.js')
        domid = field.dom_id(form, self.suffix)
        data = self.data_initfunc(form, field)
        category = req._("Similar entities:")
        data = json_dumps([{"label": item, "category": category} for sublist in data
                           for item in sublist])
        req.add_onload(u'cw.jqNode("%s").check_similar_values({source: %s});' % (domid, data))
        return super(TextInputCheckSimilar, self)._render(form, field, render)


def get_record_names(form, field):
    """Return names of all the authority records already existing"""
    return form._cw.execute('Any N WHERE A name N, A is AuthorityRecord').rows

affk.set_field_kwargs('AuthorityRecord', 'name',
                      widget=TextInputCheckSimilar({'size': 80}, data_initfunc=get_record_names))


def unrelated_authorityrecord(rtype, form, field, **kwargs):
    """Choices function returning AuthorityRecord choices.

    Choices values are unrelated through `rtype` to edited entity thus
    filtering out possible ExternalURI targets. It also account for __linkto
    info to build a restricted choice when needed.
    """
    try:
        linkto = form.linked_to[rtype, 'subject'][0]
    except (KeyError, IndexError):
        rset = form.edited_entity.unrelated(rtype, targettype='AuthorityRecord')
        return [(x.dc_title(), unicode(x.eid)) for x in rset.entities()]
    else:
        entity = form._cw.entity_from_eid(linkto)
        return [(entity.dc_title(), unicode(entity.eid))]


# Set fields order for authority records relations (autoform and primary view)
for etype, from_rdef, to_rdef in (
    ('AssociationRelation', 'association_from', 'association_to'),
    ('ChronologicalRelation', 'chronological_predecessor', 'chronological_successor'),
    ('HierarchicalRelation', 'hierarchical_parent', 'hierarchical_child'),
):
    affk.set_fields_order(etype, ('description', 'start_date', 'end_date',
                                  from_rdef, to_rdef))
    for rtype in (from_rdef, to_rdef):
        affk.tag_subject_of((etype, rtype, '*'),
                            {'choices': partial(unrelated_authorityrecord, rtype)})

    for index, attr in enumerate(('description', 'start_date',
                                  'end_date', from_rdef, to_rdef)):
        pvds.tag_attribute((etype, attr), {'order': index})

afs.tag_object_of(('*', 'authority_record', 'AuthorityRecord'), 'main', 'hidden')

# Hide computed relations (See CubicWeb ticket #4903918).
afs.tag_subject_of(('AuthorityRecord', 'postal_address', 'PostalAddress'), 'main', 'hidden')
afs.tag_object_of(('AuthorityRecord', 'postal_address', 'PostalAddress'), 'main', 'hidden')

pvs.tag_subject_of(('AuthorityRecord', 'postal_address', '*'), 'hidden')

# Hide relation to the record for these entity types edition form.
for etype, rtype in (
    ('AgentPlace', 'place_agent'),
    ('AgentFunction', 'function_agent'),
    ('LegalStatus', 'legal_status_agent'),
    ('Mandate', 'mandate_agent'),
    ('History', 'history_agent'),
    ('Structure', 'structure_agent'),
    ('Occupation', 'occupation_agent'),
    ('GeneralContext', 'general_context_of'),
    ('EACSource', 'source_agent'),
    ('EACResourceRelation', 'resource_relation_agent'),
):
    afs.tag_subject_of((etype, rtype, '*'), 'main', 'hidden')


class XMLWrapComponent(component.EntityCtxComponent):
    """CtxComponent to display xml_wrap of entities."""
    __select__ = (
        component.EntityCtxComponent.__select__
        & score_entity(lambda x: getattr(x, 'xml_wrap', None))
    )
    __regid__ = 'saem_ref.xml_wrap'
    context = 'navcontentbottom'
    title = _('xml_wrap')

    def render_body(self, w):
        sourcemt, targetmt = 'text/xml', 'text/html'
        data = self.entity.xml_wrap
        w(self.entity._cw_mtc_transform(data.getvalue(),
                                        sourcemt, targetmt, 'utf-8'))


class AuthorityRecordICalendarableAdapter(calendar.ICalendarableAdapter):
    """ICalendarable adapter for AuthorityRecord entity type."""
    __select__ = calendar.ICalendarableAdapter.__select__ & is_instance('AuthorityRecord')

    @property
    def start(self):
        return self.entity.start_date

    @property
    def stop(self):
        return self.entity.end_date


# AuthorityRecord primary views (tabs)

actions.CopyAction.__select__ &= ~is_instance('AuthorityRecord')

pvds.tag_subject_of(('AuthorityRecord', 'agent_kind', '*'), {'vid': 'text'})


class AuthorityRecordTabbedPrimaryView(tabs.TabbedPrimaryView):
    """Tabbed primary view for AuthorityRecord"""
    __select__ = tabs.TabbedPrimaryView.__select__ & is_instance('AuthorityRecord')
    tabs = [
        _('saem_ref_authorityrecord_general_information'),
        _('saem_ref_authorityrecord_description'),
        _('saem_ref_authorityrecord_properties'),
        _('saem_ref_authorityrecord_relations'),
        _('saem_ref_authorityrecord_lifecycle'),
    ]
    default_tab = 'saem_ref_authorityrecord_general_information'


# Citation
pvds.tag_attribute(('Citation', 'uri'), {'vid': 'urlattr'})
# Generic rules for all entity types having an `has_citation` relationship.
abaa.tag_subject_of(('*', 'has_citation', '*'), False)
afs.tag_subject_of(('*', 'has_citation', '*'), 'main', 'inlined')
pvs.tag_object_of(('*', 'has_citation', 'Citation'), 'hidden')


class CitationLinkView(EntityView):
    __regid__ = 'citation-link'
    __select__ = is_instance('Citation')

    def entity_call(self, entity):
        if entity.uri:
            title = entity.note or entity.uri
            desc = cut(entity.note or u'', 50)
            self.w(u'<a class="truncate" href="%s" title="%s">%s</a>' % (
                xml_escape(entity.uri), xml_escape(desc),
                xml_escape(title)))
        else:
            title = (entity.note or
                     u'{0} #{1}'.format(self._cw._('Citation'), entity.eid))
            self.w(u'<i class="truncate">%s</i>' % title)


# In the main tab.

class AuthorityRecordPrimaryTab(tabs.PrimaryTab):
    """Main tab for authority record, just with a different regid."""
    __regid__ = 'saem_ref_authorityrecord_general_information'


class TextAttributeView(EntityView):
    """View for displaying an entity's text attribute.

    This view should be call with a ``text_attr`` parameter indicating which attribute on the entity
    contains the textual information and will display this information in a ``<div>``.

    Additionally, edit buttons will be shown floating right if user has relevant permissions. And if
    ``icon_info`` parameter is ``True``, user will also see an info button redirecting to the entity
    primary view.
    """

    __regid__ = 'saem.text_attribute'
    __select__ = EntityView.__select__ & match_kwargs('text_attr')

    @editlinks(icon_info=False)
    def entity_call(self, entity, text_attr):
        self._cw.add_js(('jquery.js', 'jquery.expander.js', 'cubes.saem_ref.js'))
        self.w(tags.div(entity.printable_value(text_attr), klass='truncate'))


class AsConceptEntityView(EntityView):
    """View for displaying an entity as a SKOS concept (to which the entity is related).

    This view should be called with ``concept_rtype`` indicating the relation to ``Concept`` entity
    type. This relation should have ``1`` or ``?`` cardinality (that is, the entity should be
    related to at most one concept)

    The view will then display a link to concept URI. The link content will be the entity`s
    ``text_attr`` attribute, or the concept label as a fallback.

    Additionally, edit buttons will be shown floating right if user has relevant permissions.
    """

    __regid__ = 'saem.entity_as_concept'
    __select__ = EntityView.__select__ & match_kwargs('concept_rtype', 'text_attr')

    @editlinks(icon_info=False)
    def entity_call(self, entity, concept_rtype, text_attr, details_attr=None,
                    **kwargs):
        # Get related concept label and uri and associated scheme title and uri
        rset = entity.related(concept_rtype)
        concept = rset.one() if rset else None
        # Compute link content
        link_content = entity.printable_value(text_attr)
        if not link_content and concept:  # empty text_attr => use concept label
            link_content = xml_escape(concept.label())
        if not link_content:  # empty text_attr, no label => empty title
            link_content = u''

        if concept:
            link = external_link(link_content, cwuri_url(concept))
            self.w(u'<strong>{0}</strong>'.format(link))
        else:
            self.w(u'<strong>{0}</strong>'.format(tags.span(link_content, escapecontent=False)))
        if concept and concept.cw_etype == 'Concept':  # Could be ExternalURI
            scheme = concept.in_scheme[0]
            source_content = u'{0}: {1}'.format(
                tags.span(self._cw._('vocabulary_source')),
                external_link(scheme.title, cwuri_url(scheme)))
            self.w(tags.div(source_content, klass='small'))
        # Compute details
        details = entity.printable_value(details_attr) if details_attr else None
        if not details and concept and concept.cw_etype == 'Concept':
            # if not specified but linked to a concept with a definition, show the definition
            details = concept.printable_value('definition')
        if details:
            self._cw.add_js(('jquery.js', 'jquery.expander.js', 'cubes.saem_ref.js'))
            self.w(tags.div(details, klass='help-block truncate'))


# AuthorityRecord life-cycle

class AuthorityRecordLifeCycleTab(SubviewsTabView):
    """Life-cycle tab for authority record."""
    __regid__ = 'saem_ref_authorityrecord_lifecycle'
    __select__ = EntityView.__select__ & is_instance('AuthorityRecord')
    subvids = ('prov.activity-generated',
               'prov.activity-associated-with')


# AuthorityRecord EAC-CPF description tab.

class AuthorityRecordDescriptionTab(SubviewsTabView):
    """Tab view gathering EAC-CPF description information of an AuthorityRecord"""
    __regid__ = 'saem_ref_authorityrecord_description'
    __select__ = EntityView.__select__ & is_instance('AuthorityRecord')
    subvids = (
        'saem_ref.authorityrecord.places',
        'saem_ref.authorityrecord.functions',
        'saem_ref.authorityrecord.legal_status',
        'saem_ref.authorityrecord.mandate',
        'saem_ref.authorityrecord.occupation',
        'saem_ref.authorityrecord.generalcontext',
        'saem_ref.authorityrecord.history',
        'saem_ref.authorityrecord.structure',
    )
    rtype_role_targets = [
        ('place_agent', 'object', None),
        ('function_agent', 'object', None),
        ('mandate_agent', 'object', None),
        ('occupation_agent', 'object', None),
        ('general_context_of', 'object', None),
        ('history_agent', 'object', None),
        ('structure_agent', 'object', None),
    ]


pvs.tag_object_of(('*', 'place_agent', 'AuthorityRecord'), 'hidden')
afs.tag_object_of(('*', 'place_agent', 'AuthorityRecord'), 'main', 'hidden')
abaa.tag_object_of(('*', 'place_agent', 'AuthorityRecord'), False)


class AuthorityRecordPlaceView(RelatedEntitiesListView):
    """View for AuthorityRecordPlace, to be display in the context of an AuthorityRecord"""
    __regid__ = 'saem_ref.authorityrecord.places'
    rtype = 'place_agent'
    subvid = 'saem.agent_place_as_concept'
    _('creating AgentPlace (AgentPlace place_agent AuthorityRecord %(linkto)s)')


class AuthorityRecordPlaceAsConceptView(EntityView):
    """View for displaying an agent place as a SKOS concept

    If the place is related to a SKOS concept, this view will display a link to the concept URI.

    Additionally, edit buttons will be shown floating right if user has relevant permissions.
    """

    __regid__ = 'saem.agent_place_as_concept'

    def entity_call(self, entity, **kwargs):
        # Output role if any
        role = entity.printable_value('role')
        if role:
            self.w(u'<strong>{0}: </strong>'.format(role))
        # Output place's name
        entity.view('saem.entity_as_concept', w=self.w,
                    concept_rtype='equivalent_concept', text_attr='name',
                    **kwargs)
        # Output address details if they exists
        address = entity.place_address[0] if entity.place_address else None
        if address:
            self._cw.view('incontext', rset=address.as_rset(), w=self.w)


pvs.tag_object_of(('*', 'function_agent', 'AuthorityRecord'), 'hidden')
afs.tag_object_of(('*', 'function_agent', 'AuthorityRecord'), 'main', 'hidden')
abaa.tag_object_of(('*', 'function_agent', 'AuthorityRecord'), False)


class AuthorityRecordFunctionView(RelatedEntitiesListView):
    """View for AgentFunction, to be display in the context of an AuthorityRecord"""
    __regid__ = 'saem_ref.authorityrecord.functions'
    rtype = 'function_agent'
    subvid = 'saem.entity_as_concept'
    subvid_kwargs = {'concept_rtype': 'equivalent_concept', 'text_attr': 'name',
                     'details_attr': 'description'}
    _('creating AgentFunction (AgentFunction function_agent AuthorityRecord %(linkto)s)')


pvs.tag_object_of(('*', 'mandate_agent', 'AuthorityRecord'), 'hidden')
afs.tag_object_of(('*', 'mandate_agent', 'AuthorityRecord'), 'main', 'hidden')
abaa.tag_object_of(('*', 'mandate_agent', 'AuthorityRecord'), False)


class AuthorityRecordMandateView(RelatedEntitiesListView):
    """View for Mandate, to be displayed in the context of an AuthorityRecord"""
    __regid__ = 'saem_ref.authorityrecord.mandate'
    rtype = 'mandate_agent'
    subvid = 'saem.entity_as_concept'
    subvid_kwargs = {'concept_rtype': 'equivalent_concept',
                     'text_attr': 'term',
                     'details_attr': 'description'}
    _('creating Mandate (Mandate mandate_agent AuthorityRecord %(linkto)s)')


pvs.tag_object_of(('*', 'occupation_agent', 'AuthorityRecord'), 'hidden')
afs.tag_object_of(('*', 'occupation_agent', 'AuthorityRecord'), 'main', 'hidden')
abaa.tag_object_of(('*', 'occupation_agent', 'AuthorityRecord'), False)


class AuthorityRecordOccupationView(RelatedEntitiesListView):
    """View for Occupation, to be displayed in the context of an AuthorityRecord"""
    __regid__ = 'saem_ref.authorityrecord.occupation'
    rtype = 'occupation_agent'
    subvid = 'saem.entity_as_concept'
    subvid_kwargs = {'concept_rtype': 'equivalent_concept',
                     'text_attr': 'term',
                     'details_attr': 'description'}
    _('creating Occupation (Occupation occupation_agent AuthorityRecord %(linkto)s)')


pvs.tag_object_of(('*', 'general_context_of', 'AuthorityRecord'), 'hidden')
afs.tag_object_of(('*', 'general_context_of', 'AuthorityRecord'), 'main', 'hidden')
abaa.tag_object_of(('*', 'general_context_of', 'AuthorityRecord'), False)


class GeneralContextView(RelatedEntitiesListView):
    """View for GeneralContext, to be displayed in the context of an AuthorityRecord"""
    __regid__ = 'saem_ref.authorityrecord.generalcontext'
    rtype = 'general_context_of'
    subvid = 'saem.text_attribute'
    subvid_kwargs = {'text_attr': 'content'}
    _('creating GeneralContext (GeneralContext general_context_of AuthorityRecord %(linkto)s)')


class WithCitationViewMixIn(object):
    """View mixin displaying citation information."""
    __select__ = has_related_entities('has_citation')

    def entity_call(self, entity, *args, **kwargs):
        super(WithCitationViewMixIn, self).entity_call(entity, *args, **kwargs)
        rset = entity.related('has_citation')
        if rset:
            self.w(tags.div(u' '.join([self._cw._('Citation_plural'),
                                       self._cw.view('csv', rset,
                                                     subvid='citation-link')]),
                            klass='small'))


class WithCitationAsConceptEntityView(WithCitationViewMixIn, AsConceptEntityView):
    """Extend entity_as_concept view when entity has related citations."""
    __select__ = AsConceptEntityView.__select__ & WithCitationViewMixIn.__select__


class WithCitationTextAttributeView(WithCitationViewMixIn, TextAttributeView):
    """Extend text_attribute view when entity has related citations."""
    __select__ = TextAttributeView.__select__ & WithCitationViewMixIn.__select__


pvs.tag_object_of(('*', 'legal_status_agent', 'AuthorityRecord'), 'hidden')
afs.tag_object_of(('*', 'legal_status_agent', 'AuthorityRecord'), 'main', 'hidden')
abaa.tag_object_of(('*', 'legal_status_agent', 'AuthorityRecord'), False)


class AuthorityRecordLegalStatusView(RelatedEntitiesListView):
    """View for LegalStatus, to be displayed in the context of an AuthorityRecord"""
    __regid__ = 'saem_ref.authorityrecord.legal_status'
    rtype = 'legal_status_agent'
    subvid = 'saem.entity_as_concept'
    subvid_kwargs = {'concept_rtype': 'equivalent_concept', 'text_attr': 'term',
                     'details_attr': 'description'}
    _('creating LegalStatus (LegalStatus legal_status_agent AuthorityRecord %(linkto)s)')


pvs.tag_object_of(('*', 'history_agent', 'AuthorityRecord'), 'hidden')
afs.tag_object_of(('*', 'history_agent', 'AuthorityRecord'), 'main', 'hidden')
abaa.tag_object_of(('*', 'history_agent', 'AuthorityRecord'), False)


class AuthorityRecordHistoryView(RelatedEntitiesListView):
    """View for History, to be displayed in the context of an AuthorityRecord"""
    __regid__ = 'saem_ref.authorityrecord.history'
    rtype = 'history_agent'
    subvid = 'saem.text_attribute'
    subvid_kwargs = {'text_attr': 'text'}
    _('creating History (History history_agent AuthorityRecord %(linkto)s)')


pvs.tag_object_of(('*', 'structure_agent', 'AuthorityRecord'), 'hidden')
afs.tag_object_of(('*', 'structure_agent', 'AuthorityRecord'), 'main', 'hidden')
abaa.tag_object_of(('*', 'structure_agent', 'AuthorityRecord'), False)


class AuthorityRecordStructureView(RelatedEntitiesListView):
    """View for Structure, to be displayed in the context of an AuthorityRecord"""
    __regid__ = 'saem_ref.authorityrecord.structure'
    rtype = 'structure_agent'
    subvid = 'saem.text_attribute'
    subvid_kwargs = {'text_attr': 'description'}
    _('creating Structure (Structure structure_agent AuthorityRecord %(linkto)s)')


# AuthorityRecord views ###############################

class SaemListItemView(EntityView):
    """List item view working with tabid keyword argument."""
    __regid__ = 'saem.listitem'

    @editlinks(icon_info=False)
    def entity_call(self, entity, **kwargs):
        entity.view('listitem', w=self.w)

# AuthorityRecord EAC-CPF "control" (a.k.a. "properties") tab.


class AuthorityRecordPropertiesTab(SubviewsTabView):
    """Tab view gathering EAC-CPF controle information of an AuthorityRecord"""
    __regid__ = 'saem_ref_authorityrecord_properties'
    __select__ = EntityView.__select__ & is_instance('AuthorityRecord')
    subvids = (
        'saem_ref.authorityrecord.sources',
        'saem_ref.authorityrecord.eac_resource_relation',
    )
    rtype_role_targets = [
        ('source_agent', 'object', None),
        ('resource_relation_agent', 'object', None),
    ]


pvs.tag_object_of(('*', 'source_agent', 'AuthorityRecord'), 'hidden')
afs.tag_object_of(('*', 'source_agent', 'AuthorityRecord'), 'main', 'hidden')
abaa.tag_object_of(('*', 'source_agent', 'AuthorityRecord'), False)

pvds.tag_attribute(('EACSource', 'url'), {'vid': 'urlattr'})


class AuthorityRecordEACSourceView(RelatedEntitiesListView):
    """View for EACSource, to be display in the context of an AuthorityRecord"""
    __regid__ = 'saem_ref.authorityrecord.sources'
    rtype = 'source_agent'
    subvid = 'saem.eacsource-listitem'
    _('creating EACSource (EACSource source_agent AuthorityRecord %(linkto)s)')


class EACSourceListItemView(EntityView):
    """List item view for EACSource."""

    __regid__ = 'saem.eacsource-listitem'
    __select__ = has_related_entities('source_agent', role='subject')

    @editlinks(icon_info=False)
    def entity_call(self, entity):
        if entity.title:
            self.w(tags.h5(entity.title, klass='list-group-item-heading'))
        if entity.description:
            self.w(u'<p class="list-group-item-text">{0}</p>'.format(
                entity.printable_value('description')))
        if entity.url:
            entity.view('saem.external_link', rtype='url', w=self.w)


pvs.tag_object_of(('*', 'resource_relation_agent', 'AuthorityRecord'), 'hidden')
afs.tag_object_of(('*', 'resource_relation_agent', 'AuthorityRecord'), 'main', 'hidden')
abaa.tag_object_of(('*', 'resource_relation_agent', 'AuthorityRecord'), False)

pvds.tag_subject_of(('EACResourceRelation', 'resource_relation_resource', '*'),
                    {'vid': 'saem.external_link'})


class AuthorityRecordEACResourceRelationView(RelatedEntitiesListView):
    """View for EACResourceRelation, to be displayed in the context of an AuthorityRecord"""
    __regid__ = 'saem_ref.authorityrecord.eac_resource_relation'
    rtype = 'resource_relation_agent'
    subvid = 'saem.eacresource-listitem'
    _('creating EACResourceRelation (EACResourceRelation '
      'resource_relation_agent AuthorityRecord %(linkto)s)')


class EACResourceListItemView(EntityView):
    """List item view for EACResource."""

    __regid__ = 'saem.eacresource-listitem'
    __select__ = has_related_entities('resource_relation_agent', role='subject')

    @editlinks(icon_info=False)
    def entity_call(self, entity, **kwargs):
        resource_role = entity.printable_value('resource_role')
        resource = entity.resource
        title = u' '.join([resource_role, resource.view('saem.external_link')])
        self.w(tags.h5(title, escapecontent=False,
                       klass='list-group-item-heading'))
        if entity.agent_role:
            self.w(u'<p class="list-group-item-text"><em>{0}</em> {1}</p>'.format(
                self._cw._('agent_role'), entity.printable_value('agent_role')))
        if entity.description:
            self.w(u'<p class="list-group-item-text">{0}</p>'.format(
                entity.printable_value('description')))
        if entity.start_date or entity.end_date:
            self.w(u'<p class="list-group-item-text">{0} - {1}</p>'.format(
                entity.printable_value('start_date'),
                entity.printable_value('end_date')))


# AuthorityRecord relations tab.

class AuthorityRecordRelationsTab(SubviewsTabView):
    """Tab view for AuthorityRecord relations."""
    __regid__ = 'saem_ref_authorityrecord_relations'
    __select__ = EntityView.__select__ & is_instance('AuthorityRecord')
    subvids = (
        'saem_ref.authorityrecord.association_relations',
        'saem_ref.authorityrecord.chronological_relation',
        'saem_ref.authorityrecord.hierarchical-links',
    )
    rtype_role_targets = [
        ('chronological_predecessor', 'object', None),
        ('chronological_successor', 'object', None),
        ('hierarchical_child', 'object', None),
        ('hierarchical_parent', 'object', None),
        ('association_from', 'object', None),
    ]


pvs.tag_object_of(('*', 'association_from', 'AuthorityRecord'), 'hidden')
afs.tag_object_of(('*', 'association_from', 'AuthorityRecord'), 'main', 'hidden')
pvs.tag_object_of(('*', 'association_to', 'AuthorityRecord'), 'hidden')
afs.tag_object_of(('*', 'association_to', 'AuthorityRecord'), 'main', 'hidden')


class AuthorityRecordAssociationRelationView(EntityView):
    """View for association relations to be displayed in the context of an
    AuthorityRecord on either the `from` or `to` side of the relation.
    """
    __regid__ = 'saem_ref.authorityrecord.association_relations'
    __select__ = EntityView.__select__ & (
        has_related_entities('association_from', role='object') |
        has_related_entities('association_to', role='object'))

    def entity_call(self, entity, **kwargs):
        self.w(tags.h2(self._cw._('associated with')))
        rset = self._cw.execute(
            '(Any X WHERE X association_from A, A eid %(eid)s) '
            'UNION (Any X WHERE X association_to A, A eid %(eid)s)',
            {'eid': entity.eid})
        self._cw.view('list', rset=rset, w=self.w,
                      subvid='saem_ref.associationrelation',
                      main_record=entity,
                      __redirectpath=entity.rest_path())


class AssociationRelationView(EntityView):
    """Extended 'oneline' view for AssociationRelation"""
    __regid__ = 'saem_ref.associationrelation'
    __select__ = (EntityView.__select__ &
                  is_instance('AssociationRelation') & match_kwargs('main_record'))

    _('creating AssociationRelation (AssociationRelation association_from '
      'AuthorityRecord %(linkto)s)')

    @editlinks(icon_info=True)
    def entity_call(self, entity, main_record):
        for other_record in (entity.association_from[0], entity.association_to[0]):
            if other_record != main_record:
                self.w(other_record.view('outofcontext'))
                break
        if entity.start_date or entity.end_date:
            self.w(tags.span(u' ({0}-{1})'.format(entity.printable_value('start_date'),
                                                  entity.printable_value('end_date')),
                             klass='text-muted'))
        if entity.description:
            self.w(tags.div(entity.printable_value('description')))


pvs.tag_object_of(('*', 'chronological_predecessor', 'AuthorityRecord'), 'hidden')
afs.tag_object_of(('*', 'chronological_predecessor', 'AuthorityRecord'), 'main', 'hidden')
pvs.tag_object_of(('*', 'chronological_successor', 'AuthorityRecord'), 'hidden')
afs.tag_object_of(('*', 'chronological_successor', 'AuthorityRecord'), 'main', 'hidden')


class ChronologicalRelationView(EntityView):
    """Timeline view with authority records involved in a ChronologicalRelation with this authority
    record entity.
    """
    __regid__ = 'saem_ref.authorityrecord.chronological_relation'
    __select__ = EntityView.__select__ & (
        has_related_entities('chronological_successor', role='object') |
        has_related_entities('chronological_predecessor', role='object'))
    title = _('ChronologicalRelation_plural')
    _("creating ChronologicalRelation (ChronologicalRelation "
      "chronological_predecessor AuthorityRecord %(linkto)s)")
    _("creating ChronologicalRelation (ChronologicalRelation "
      "chronological_successor AuthorityRecord %(linkto)s)")

    def entity_call(self, entity, **kwargs):
        self.w(tags.h2(self._cw._(self.title).lower()))
        rset = self._cw.execute('(Any X WHERE X eid %(eid)s) '
                                'UNION (Any S WHERE RP chronological_predecessor X, '
                                '       RP chronological_successor S, X eid %(eid)s) '
                                'UNION (Any P WHERE RS chronological_successor X, '
                                '       RS chronological_predecessor P, X eid %(eid)s)',
                                {'eid': entity.eid})
        json_url = self._cw.build_url('view', rql=entity.as_rset().printable_rql(),
                                      vid='saem_ref.authorityrecord-timeline-json')
        self._cw.view('vtimeline', rset=rset, w=self.w, custom_settings={'source': json_url})


class AuthorityRecordTimelineJsonView(EntityView):
    """JSON view for agent with chronological relations to be used with vtimeline view."""
    __regid__ = 'saem_ref.authorityrecord-timeline-json'
    __select__ = adaptable('ICalendarable') & is_instance('AuthorityRecord')
    template = False
    content_type = 'application/json'
    binary = True

    headers = {
        'headline': '',
        'type': 'default',
        'text': '',
        'asset': {},
    }

    def entity_call(self, entity):
        data = dict(self.headers)
        data['date'] = [
            self.entity_as_date(entity, tag=self._cw._('subject'),
                                text=entity.dc_description()),
        ]
        if entity.reverse_chronological_successor:
            relation = entity.reverse_chronological_successor[0]
            predecessor = relation.chronological_predecessor[0]
            data['date'].append(self.entity_as_date(
                predecessor,
                text=relation.view('saem_ref.timeline-item',
                                   __redirectpath=entity.rest_path()),
                tag=self._cw._('chronological_predecessor'))
            )
        if entity.reverse_chronological_predecessor:
            relation = entity.reverse_chronological_predecessor[0]
            successor = relation.chronological_successor[0]
            data['date'].append(self.entity_as_date(
                successor,
                text=relation.view('saem_ref.timeline-item',
                                   __redirectpath=entity.rest_path()),
                tag=self._cw._('chronological_successor'))
            )
        self.w(json_dumps({'timeline': data}))

    @staticmethod
    def entity_as_date(entity, **kwargs):
        """Return a dict suitable for insertion within the `date` entry of
        TimelineJS JSON structure.
        """
        date = {}
        calendarable = entity.cw_adapt_to('ICalendarable')
        if calendarable and (calendarable.start or calendarable.stop):
            date.update(
                {'headline': entity.view('incontext'),
                 'text': entity.view('vtimeline-itemdescr')}
            )
            if calendarable.start:
                date['startDate'] = ustrftime(calendarable.start, '%Y,%m,%d')
            if calendarable.stop:
                date['endDate'] = ustrftime(calendarable.stop, '%Y,%m,%d')
        date.update(kwargs)
        return date


class ChronologicalRelationTimelineItemView(EntityView):
    """View for 'text' part of date event in timeline view"""
    __regid__ = 'saem_ref.timeline-item'
    __select__ = is_instance('ChronologicalRelation')

    def entity_call(self, entity, **urlparams):
        self.w(entity.printable_value('description'))
        vreg = self._cw.vreg
        eschema = vreg.schema.eschema(entity.cw_etype)
        if eschema.has_perm(self._cw, 'update'):
            self.w(tags.a(title=self._cw._('edit'), klass='icon-pencil',
                          href=entity.absolute_url('edition', **urlparams)))


def _node(entity, rel=None):
    req = entity._cw
    if rel is not None:
        url = entity.absolute_url()
        descr = rel.printable_value('description', format='text/plain')
        if descr:
            descr_url_desc = descr
            descr = cut(descr, 100)
        else:
            descr = req._('<no description specified>')
            descr_url_desc = req._('view this relation')
        descr_url = rel.absolute_url()
        dates = []
        if rel.start_date:
            dates.append(rel.printable_value('start_date'))
        if rel.end_date:
            dates.append(rel.printable_value('end_date'))
    else:
        url = descr = descr_url = descr_url_desc = dates = u''
    title = entity.dc_title()
    return {
        'id': unicode(entity.eid),
        'title': cut(title, 30),
        'title_url': url,
        'title_url_desc': title,
        'descr': descr,
        'descr_url': descr_url,
        'descr_url_desc': descr_url_desc,
        'dates': u' - '.join(dates),
    }


def _add_html_node_content(properties):
    return (u'<p>%(title)s</p><p>%(descr)s</p><p class="dates">%(dates)s</p>' %
            {'title': tags.a(properties['title'], href=properties['title_url'], klass=u'title'),
             'descr': tags.a(properties['descr'], href=properties['descr_url']),
             'dates': properties['dates']})


class AuthorityRecordGraphView(EntityView):
    __select__ = EntityView.__select__ & (
        has_related_entities('hierarchical_parent', role='object') |
        has_related_entities('hierarchical_child', role='object'))

    __regid__ = 'saem_ref.authorityrecord.hierarchical-links'
    title = _('HierarchicalRelation_plural')

    _('creating HierarchicalRelation (HierarchicalRelation hierarchical_child '
      'AuthorityRecord %(linkto)s)')
    _('creating HierarchicalRelation (HierarchicalRelation hierarchical_parent '
      'AuthorityRecord %(linkto)s)')

    def entity_call(self, entity, **kwargs):
        self.w(tags.h2(self._cw._(self.title).lower()))
        self._cw.add_js(('jquery.js', 'jquery.jOrgChart.js'))
        self._cw.add_css('jquery.jOrgChart.css')
        hiera_list = u'<ul id="hierarchical_relations" style="display:none">'
        tags_closure = u'</ul>'
        rset_parents = self._cw.execute('Any P, PR WHERE PR hierarchical_child X, '
                                        'PR hierarchical_parent P, X eid %s' % entity.eid)
        if rset_parents:
            parent = rset_parents.get_entity(0, 0)
            parent_rel = rset_parents.get_entity(0, 1)
            nprops = _node(parent, parent_rel)
            hiera_list += u'<li>' + _add_html_node_content(nprops) + u'<ul>'
            tags_closure = u'</ul></li>' + tags_closure
        nprops = _node(entity)
        hiera_list += u'<li class="main">' + _add_html_node_content(nprops) + u'<ul>'
        tags_closure = u'</ul></li>' + tags_closure
        for child_rel in entity.reverse_hierarchical_parent:
            for child in child_rel.hierarchical_child:
                nprops = _node(child, child_rel)
                hiera_list += u'<li>' + _add_html_node_content(nprops) + u'</li>'
        hiera_list += tags_closure
        self.w(hiera_list)
        domid = make_uid()
        self._cw.add_onload(js.cw.jqNode('hierarchical_relations').jOrgChart(
            JSString('{chartElement: %s}' % js.cw.jqNode(domid))))
        self.w(u'<div id="%s"></div>' % domid)
        if len(rset_parents) > 1:
            self.w(u'<div class="other-parents icon-attention">')
            self.w(self._cw._('AuthorityRecord %s has several parents:') % entity.name)
            self._cw.view('list', rset_parents, w=self.w)
            self.w(u'</div>')


pvs.tag_object_of(('*', 'hierarchical_parent', 'AuthorityRecord'), 'hidden')
afs.tag_object_of(('*', 'hierarchical_parent', 'AuthorityRecord'), 'main', 'hidden')

pvs.tag_object_of(('*', 'hierarchical_child', 'AuthorityRecord'), 'hidden')
afs.tag_object_of(('*', 'hierarchical_child', 'AuthorityRecord'), 'main', 'hidden')

# AgentPlace
afs.tag_subject_of(('AgentPlace', 'place_address', 'PostalAddress'),
                   'main', 'inlined')

# AgentFunction
affk.set_field_kwargs('AgentFunction', 'name', widget=fw.TextInput({'size': 80}))
