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
"""cubicweb-saem-ref specific hooks and operations"""

from datetime import datetime

from logilab.common.registry import objectify_predicate

from yams import ValidationError
from yams.schema import role_name

from cubicweb.schema import META_RTYPES
from cubicweb.predicates import is_instance, adaptable, on_fire_transition
from cubicweb.server import hook
from cubicweb.hooks import metadata

from cubes.skos.hooks import ReplaceExternalUriByEntityHook
from cubes.saem_ref.entities import container

_ = unicode

# skip relation involved in the logging itself, or mirroring relation
IGNORE_RELATIONS = set(('used', 'generated', 'associated_with', 'mirror_of'))


@objectify_predicate
def contained_relation(cls, req, rtype, eidfrom, eidto, **kwargs):
    """Predicate that returns True for relation from/to a container or contained entity.
    """
    if rtype in IGNORE_RELATIONS:
        return 0
    for eid in (eidfrom, eidto):
        entity = req.entity_from_eid(eid)
        for interface in ('IContainer', 'IContained'):
            if entity.cw_adapt_to(interface):
                # skip meta relation of contained entities, only consider them on the container
                if interface == 'IContained' and rtype in META_RTYPES:
                    return 0
                return 1
    return 0


def qualify_relation(subj, rtype, obj):
    """Return a list of (relationship, role, target) qualifying the relation.

    Options are:

    * `relationship` = 'parent' and `target` the parent entity adapter
    * `relationship` = 'border' and `target` the container or contained adapter

    In both cases `role` is the role of the target in the relation.
    """
    # first attempt to get the more specific adapter for subject and object of the relation
    for interface in ('IContainer', 'IContained'):
        s_adapter = subj.cw_adapt_to(interface)
        if s_adapter is not None:
            break
    for interface in ('IContainer', 'IContained'):
        o_adapter = obj.cw_adapt_to(interface)
        if o_adapter is not None:
            break
    # then check if the relation is a parent relation
    if (s_adapter is not None and s_adapter.__regid__ == 'IContained'
            and (rtype, 'subject') in s_adapter.parent_relations):
        assert o_adapter, ('parent relation %s of contained entity #%d does not link to a '
                           'IContainer/IContained entity' % (rtype, subj.eid))
        return [('parent', 'object', o_adapter)]
    if (o_adapter is not None and o_adapter.__regid__ == 'IContained'
            and (rtype, 'object') in o_adapter.parent_relations):
        assert s_adapter, ('parent relation %s of contained entity #%d does not link to a '
                           'IContainer/IContained entity' % (rtype, obj.eid))
        return [('parent', 'subject', s_adapter)]
    # from here, we can assume rtype is not a parentship relation. Notice the relation may concerns
    # to distinct container
    assert s_adapter or o_adapter
    result = []
    if s_adapter is not None:
        result.append(('border', 'subject', s_adapter))
    if o_adapter is not None:
        result.append(('border', 'object', o_adapter))
    return result


# generic hooks to record operations if something changed in a compound tree ###

class AddOrRemoveChildrenHook(hook.Hook):
    """Some relation involved in a compound graph is added or removed."""
    __regid__ = 'compound.graph.updated'
    __select__ = hook.Hook.__select__ & contained_relation()
    events = ('before_add_relation', 'before_delete_relation')
    category = 'metadata'

    def __call__(self):
        for relationship, role, target in qualify_relation(self._cw.entity_from_eid(self.eidfrom),
                                                           self.rtype,
                                                           self._cw.entity_from_eid(self.eidto)):
            entity = target.entity
            UpdateModificationDateOp.get_instance(self._cw).add_entity(entity)
            if entity.cw_etype in container.PROFILE_CONTAINER_DEF:
                CheckProfileSEDACompatiblityOp.get_instance(self._cw).add_entity(entity)


class UpdateEntityHook(hook.Hook):
    """Some entity involved in a compound graph is updated."""
    __regid__ = 'compound.graph.updated'
    __select__ = hook.Hook.__select__ & adaptable('IContainer', 'IContained')
    events = ('before_update_entity',)
    category = 'metadata'

    def __call__(self):
        UpdateModificationDateOp.get_instance(self._cw).add_entity(self.entity)
        if self.entity.cw_etype in container.PROFILE_CONTAINER_DEF:
            CheckProfileSEDACompatiblityOp.get_instance(self._cw).add_entity(self.entity)


# Auto-update of modification date in a compound tree ##########################

class UpdateModificationDateOp(hook.DataOperationMixIn, hook.Operation):
    """Data operation updating the modification date of its data entities."""

    def precommit_event(self):
        cnx = self.cnx
        now = datetime.utcnow()
        with cnx.deny_all_hooks_but():
            for eid in self.get_data():
                if cnx.deleted_in_transaction(eid) or cnx.added_in_transaction(eid):
                    continue
                entity = cnx.entity_from_eid(eid)
                entity.cw_set(modification_date=now)

    def add_entity(self, entity):
        """Add entity, its parent entities (up to the container root) for update of their
        modification date at commit time.
        """
        self.add_data(entity.eid)
        while True:
            safety_belt = set((entity.eid,))
            contained = entity.cw_adapt_to('IContained')
            if contained is None:
                assert entity.cw_adapt_to('IContainer')
                break
            else:
                entity = contained.parent
                if entity is None or entity.eid in safety_belt:
                    break
                self.add_data(entity.eid)
                safety_belt.add(entity.eid)


# Transformation of ExternalUri to Agent  ######################################

class ReplaceExternalUriByAgentHook(ReplaceExternalUriByEntityHook):
    """Replace ExternalUri by an Agent"""
    __select__ = ReplaceExternalUriByEntityHook.__select__ & is_instance('Agent')


# ARK generation ###############################################################

class AssignARKToSKOSHook(hook.Hook):
    """when an agent, SEDA profile, scheme or concept is created, assign a local ark to it"""
    __regid__ = 'saem_ref.ark.assign'
    __select__ = hook.Hook.__select__ & is_instance('Agent', 'SEDAProfile',
                                                    'ConceptScheme', 'Concept')
    events = ('before_add_entity',)
    order = metadata.InitMetaAttrsHook.order - 1

    def __call__(self):
        if not self.entity.cw_edited.get('ark'):
            naa_what = self.entity.cw_adapt_to('IArkNAALocator').naa_what()
        else:
            naa_what = None
        set_ark_and_cwuri(self._cw, self.entity.eid, self.entity.cw_etype,
                          self.entity.cw_edited, naa_what=naa_what)


def set_ark_and_cwuri(cw, eid, etype, entity_attrs, naa_what=None):
    ark = entity_attrs.get('ark')
    if not ark:
        cwuri = entity_attrs.get('cwuri')
        ark = None if cwuri is None else extract_ark(cwuri)
        if ark is None:
            if naa_what is None:
                msg = _('an ARK identifier has to be generated but no Name Assigning Authority is '
                        'specified')
                raise ValidationError(None, {'': msg})
            generator = cw.vreg['adapters'].select('IARKGenerator', cw, eid=eid, etype=etype,
                                                   naa_what=naa_what)
            ark = generator.generate_ark()
        entity_attrs['ark'] = ark
    if 'cwuri' not in entity_attrs:
        # store ark as cwuri, not an URL so it's easier to move the database while still easy to get
        # an URL from there (see the cwuri_url function) XXX (syt) any other reason to do so? there
        # is also probably some constraint on (re)import or something similar but I don't recall
        # right now
        entity_attrs['cwuri'] = u'ark:/' + ark


def extract_ark(url):
    """Extract ARK identifier from an URL, return it or None if not found or malformed.
    """
    try:
        _, ark = url.split('ark:/', 1)
    except ValueError:
        return None
    parts = ark.split('/')
    if len(parts) < 2:
        return None
    ark = '/'.join(parts[:2])
    for delim in '#?':
        ark = ark.split(delim, 1)[0]
    return ark


# Life-cycle logging ###########################################################

class Record(object):
    """Temporary representation of some activities to be recorded, for accumulation per entity
    prior to merge in an operation.
    """
    def __init__(self, events):
        if not isinstance(events, set):
            events = set(events)
        self.events = events

    def __str__(self):
        return ','.join(sorted('%s %s' % ev for ev in self.events))

    def merge(self, other):
        """Merge the activity with another."""
        self.events |= other.events

    def as_dict(self, _):
        """Return a dictionary suitable for creation of the Activity entity."""
        now = datetime.utcnow()
        record = {'start': now, 'end': now}
        # merge events on the same target
        targets_per_event_type = {}
        events_by_target = {}
        for ev_type, ev_target in self.events:
            events_by_target.setdefault(ev_target, set([])).add(ev_type)
        for target, target_events in events_by_target.iteritems():
            # if there are several event types for the same target (e.g. added and removed a
            # relation), group them into the "modified" event type
            if len(target_events) > 1:
                ev_type = 'modified'
            else:
                ev_type = iter(target_events).next()
            targets_per_event_type.setdefault(_(ev_type), []).append(target)
        # now generate proper messages for each event type
        msgs = []
        # iterates on event types to get expected order
        for ev_type in (_('created'), _('modified'), _('added'), _('removed')):
            if ev_type not in targets_per_event_type:
                continue
            modified = sorted(_(x).lower() for x in targets_per_event_type[ev_type])
            msgs.append(u'%s %s' % (ev_type, u', '.join(modified)))
        if len(msgs) == 1:
            record['description'] = msgs[0]
        else:
            record['description'] = u'\n'.join(u'* ' + msg for msg in msgs)
        # complete record with other metadata then we're done
        record['description_format'] = u'text/rest'
        record['type'] = u'create' if _('created') in targets_per_event_type else u'modify'
        return record


class AddActivityOperation(hook.DataOperationMixIn, hook.LateOperation):
    """The operation responsible to merge activites to their container then to record them."""
    def precommit_event(self):
        # translate using site default language
        lang = self.cnx.vreg.property_value('ui.language')
        _ = self.cnx.vreg.config.translations[lang][0]
        # first, merge all activities (there may be several for the same container entity)
        activity_per_container = {}
        for entity, activity in self.get_data():
            # find the entity on which we should log the activity
            icontainer = entity.cw_adapt_to('IContainer')
            if icontainer is None:
                icontainer = entity.cw_adapt_to('IContained')
                if icontainer is None:
                    # "free" entity, no logging
                    self.warning("%s is not in a container, don't record activity", entity)
                    continue
            container = icontainer.container
            # if the container is not yet linked or has been deleted in this transaction, we've
            # nothing to log on
            if container is None or self.cnx.deleted_in_transaction(container.eid):
                continue
            # if the container has been created in this transaction, discard all activities but the
            # creation
            if self.cnx.added_in_transaction(container.eid):
                if ('created', entity.cw_etype) in activity.events:
                    # only keep the creation event
                    assert container not in activity_per_container
                    activity_per_container[container] = activity
            else:
                try:
                    activity_per_container[container].merge(activity)
                except KeyError:
                    activity_per_container[container] = activity
        # who?
        if self.cnx.user.eid == -1:  # internal manager
            agent = None
        else:
            user = self.cnx.entity_from_eid(self.cnx.user.eid)
            agent = user.reverse_agent_user and user.reverse_agent_user[0] or None
        # then record the activities
        for container, activity in activity_per_container.items():
            kwargs = activity.as_dict(_)
            if agent is not None:
                kwargs.setdefault('associated_with', agent)
            adapted = container.cw_adapt_to('IRecordable')
            if adapted is not None:
                adapted.add_activity(**kwargs)


class LogContainerCreationHook(hook.Hook):
    """Add an Activity upon creation of a container entity (`IContainer`). There is no need for a
    hook on `IContained` creation, we'll catch creation of the relation linking them to their
    container.
    """
    __select__ = hook.Hook.__select__ & adaptable('IContainer')
    __regid__ = 'saem_ref.log.add'
    events = ('after_add_entity',)
    category = 'prov.logging'

    def __call__(self):
        activity = Record([('created', self.entity.cw_etype)])
        AddActivityOperation.get_instance(self._cw).add_data((self.entity, activity))


class LogModificationHook(hook.Hook):
    """Add an Activity upon modification of a container (`IContainer`) or contained (`IContained`)
    entity. The message should be adapted accordingly.
    """
    __select__ = hook.Hook.__select__ & adaptable('IContainer', 'IContained')
    __regid__ = 'saem_ref.log.update'
    events = ('after_update_entity',)
    category = 'prov.logging'

    def __call__(self):
        entity = self.entity
        if entity.cw_adapt_to('IContainer'):
            attrs = set(attr for attr in entity.cw_edited if attr not in META_RTYPES)
            if not attrs:
                return
            events = [('modified', attr) for attr in attrs]
        else:  # IContained
            parent_relation = entity.cw_adapt_to('IContained').parent_relation()
            if parent_relation is None:
                # not yet bound to a parent, skip this activity (later addition of the relation will
                # trigger the record if necessary)
                return
            rtype, role = parent_relation
            # role is the role of the entity, we want to qualify the relation by the role of the
            # parent
            if role == 'subject':
                rtype += '_object'
            events = [('modified', rtype)]
        activity = Record(events)
        AddActivityOperation.get_instance(self._cw).add_data((entity, activity))


class LogRelationHook(hook.Hook):
    """Add an Activity upon modification of a container (`IContainer`) or contained (`IContained`)
    entity. The message should be adapted accordingly.
    """
    __select__ = hook.Hook.__select__ & contained_relation()
    __regid__ = 'saem_ref.log.relation'
    events = ('after_add_relation', 'before_delete_relation')
    category = 'prov.logging'

    def __call__(self):
        for relationship, role, target in qualify_relation(self._cw.entity_from_eid(self.eidfrom),
                                                           self.rtype,
                                                           self._cw.entity_from_eid(self.eidto)):
            rtype = self.rtype
            if role == 'object':
                rtype += '_object'
            if self.event == 'after_add_relation':
                events = [('added', rtype)]
                self.add_activity(target.entity, events)
            else:  # before_delete_relation
                events = [('removed', rtype)]
                # in the case of a relation deletion, we've to find the container right away without
                # waiting for the operation since the parent relation may have been removed at this
                # point
                container = target.container
                if container is not None:
                    self.add_activity(container, events)

    def add_activity(self, entity, events):
        activity = Record(events)
        AddActivityOperation.get_instance(self._cw).add_data((entity, activity))


# SEDA ###############################################################

class CheckProfileSEDACompatiblityOp(hook.DataOperationMixIn, hook.Operation):
    """Data operation that will check compatibility of a SEDA profile upon modification."""
    seda_adapters = ['SEDA-0.2.xsd', 'SEDA-1.0.xsd']

    def precommit_event(self):
        cnx = self.cnx
        profiles = set()
        for eid in self.get_data():
            if cnx.deleted_in_transaction(eid):
                continue
            entity = cnx.entity_from_eid(eid)
            if entity.cw_etype == 'SEDAProfile':
                profiles.add(entity)
            else:
                container = entity.cw_adapt_to('IContained').container
                if container is not None:
                    profiles.add(container)
        with cnx.deny_all_hooks_but():
            for profile in profiles:
                supported = []
                for adapter_id in self.seda_adapters:
                    if profile.cw_adapt_to(adapter_id).is_compatible():
                        supported.append(adapter_id)
                profile.cw_set(support_seda_exports=u', '.join(sorted(supported)))

    def add_entity(self, entity):
        """Add entity, its parent entities (up to the container root) for update of their
        modification date at commit time.
        """
        self.add_data(entity.eid)
        while True:
            safety_belt = set((entity.eid,))
            contained = entity.cw_adapt_to('IContained')
            if contained is None:
                assert entity.cw_adapt_to('IContainer')
                break
            else:
                entity = contained.container
                if entity is None or entity.eid in safety_belt:
                    break
                self.add_data(entity.eid)
                safety_belt.add(entity.eid)


class CheckNewProfile(hook.Hook):
    """Instantiate operation checking for profile seda compat on its creation"""
    __regid__ = 'saem_ref.create-profile'
    __select__ = hook.Hook.__select__ & is_instance('SEDAProfile')
    events = ('after_add_entity', )

    def __call__(self):
        CheckProfileSEDACompatiblityOp.get_instance(self._cw).add_entity(self.entity)


class AddMandatoryRelationsToProfileArchiveHook(hook.Hook):
    """Create mandatory relations upon creation of first level ProfileArchiveObject (easing
    entity creation from the UI).
    """
    __select__ = hook.Hook.__select__ & hook.match_rtype('seda_parent', toetypes=('SEDAProfile',))
    __regid__ = 'seda.add_mandatory_relations_to_profilearchive'
    events = ('after_add_relation',)

    def __call__(self):
        document_unit = self._cw.entity_from_eid(self.eidfrom)
        if not document_unit.access_restriction_code:
            self._cw.create_entity('SEDAAccessRestrictionCode',
                                   user_cardinality=u'1',
                                   reverse_seda_access_restriction_code=document_unit)
        if not document_unit.content_description:
            desc_level = self._cw.create_entity('SEDADescriptionLevel')
            self._cw.create_entity('SEDAContentDescription',
                                   user_cardinality=u'1',
                                   seda_description_level=desc_level,
                                   reverse_seda_content_description=document_unit)


class DepreciateProfileOnReplacePublishedHook(hook.Hook):
    """Depreciate a SEDA profile once the new version is published."""
    __select__ = hook.Hook.__select__ & on_fire_transition('SEDAProfile', 'publish')
    __regid__ = 'seda.deprecate_profile_on_replace_published'
    events = ('after_add_entity',)

    def __call__(self):
        replaced = self.entity.for_entity.seda_replace
        if replaced:
            wf = replaced[0].cw_adapt_to('IWorkflowable')
            wf.fire_transition_if_possible("deprecate")


# Relations deposit agent - archival agent  ####################################

class CheckArchivalAgentRelOperation(hook.DataOperationMixIn, hook.Operation):
    def precommit_event(self):
        for agent in self.get_data():
            if agent.has_role(u'deposit'):
                if not agent.archival_agent:
                    errors = {role_name('archival_agent', 'subject'):
                              _('this relation is mandatory on deposit agents')}
                    raise ValidationError(agent.eid, errors)


class CheckArchivalAgentRelOnAddAgentHook(hook.Hook):
    """When creating an agent of type "deposit", it must have an archival_agent
    relation
    """
    __select__ = hook.Hook.__select__ & is_instance('Agent')
    __regid__ = 'saem_ref.check_archival_agent_relation_exists_add_agent'
    events = ('after_add_entity', )

    def __call__(self):
        CheckArchivalAgentRelOperation.get_instance(self._cw).add_data(self.entity)


class CheckArchivalAgentRelHookOnDeleteArchivalAgent(hook.Hook):
    """When deleting a "archival_agent" on an agent, make sure this one is not a deposit agent,
    or be linked to a new archival agent
    """
    __select__ = hook.Hook.__select__ & hook.match_rtype('archival_agent')
    __regid__ = 'saem_ref.check_archival_agent_relation_exists_del_archival_agent'
    events = ('before_delete_relation', )

    def __call__(self):
        CheckArchivalAgentRelOperation.get_instance(self._cw).add_data(
            self._cw.entity_from_eid(self.eidfrom))


class CheckArchivalAgentOnArchivalRoleUpdateHook(hook.Hook):
    """When adding a "deposit" role to an agent, make sure this agent is linked to an archival agent
    """
    __select__ = hook.Hook.__select__ & hook.match_rtype('archival_role')
    __regid__ = 'saem_ref.archival_role.add'
    events = ('after_add_relation', )

    def __call__(self):
        if self._cw.entity_from_eid(self.eidto).name == u'deposit':
            CheckArchivalAgentRelOperation.get_instance(self._cw).add_data(
                self._cw.entity_from_eid(self.eidfrom))


class DontDeleteAgentIfArchival(hook.Hook):
    """Before deleting an agent, if it is an archival agent, make sure it isn't
    associated to another agent through the "archival_agent" relation.
    """
    __select__ = hook.Hook.__select__ & hook.match_rtype('archival_role')
    __regid__ = 'saem_ref.archival_role.delete'
    events = ('before_delete_relation', )

    def __call__(self):
        agent = self._cw.entity_from_eid(self.eidfrom)
        role = self._cw.entity_from_eid(self.eidto)
        if role.name == u'archival' and agent.reverse_archival_agent:
            errors = {role_name('archival_role', 'subject'):
                      _('this agent is the archival agent of other agents, '
                        'therefore the role "archival" cannot be deleted')}
            raise ValidationError(agent.eid, errors)


# ensure that equivalent_concept Concept has vocabulary_source defined ####################

class EnsureVocabularySource(hook.Hook):
    """When a equivalent_concept relation is set and targets a Concept, ensure that the
    vocabulary_source relation is set to the concept's scheme. This should not be necessary when
    using the UI where the workflow enforce setting the scheme first, but it's necessary during
    e.g. EAC import.
    """
    __select__ = hook.Hook.__select__ & hook.match_rtype('equivalent_concept',
                                                         toetypes=('Concept',))
    __regid__ = 'saem_ref.add_equivalent_concept'
    events = ('after_add_relation', )

    def __call__(self):
        EnsureVocabularySourceOp.get_instance(self._cw).add_data((self.eidfrom, self.eidto))


class EnsureVocabularySourceOp(hook.DataOperationMixIn, hook.Operation):
    """Ensure X equivalent_concept target Concept as proper X vocabulary_source Scheme"""

    def precommit_event(self):
        cnx = self.cnx
        for eid, concept_eid in self.get_data():
            cnx.execute('SET X vocabulary_source SC WHERE NOT X vocabulary_source SC, '
                        'C in_scheme SC, C eid %(c)s, X eid %(x)s', {'x': eid, 'c': concept_eid})


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__)
    from cubicweb.server import ON_COMMIT_ADD_RELATIONS
    from cubes.saem_ref import PERMISSIONS_GRAPHS, OUTER_RELATIVE_PERM_RELATIONS, mandatory_rdefs
    # Add relations involved in a composite graph with security setup to "on
    # commit" check step.
    schema = vreg.schema
    for etype, graph_def in PERMISSIONS_GRAPHS.iteritems():
        graph = graph_def(schema)
        for rdef, _ in mandatory_rdefs(schema, graph.parent_structure(etype)):
            ON_COMMIT_ADD_RELATIONS.add(rdef.rtype)
    # As well as those whose security rules are defined in the schema directly.
    ON_COMMIT_ADD_RELATIONS.update(OUTER_RELATIVE_PERM_RELATIONS)
