import logging
import functools
from itertools import groupby

import ldap
from ldap.filter import filter_format
import ldap.modlist
import ldap.dn


from .utils import batch_generator, to_dict_of_set, idict, str2dn, istr


@functools.total_ordering
class Action(object):
    dn = None
    new_dn = None
    entry = None

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.msgids = []
        self.errors = []
        self.results = []

    def __eq__(self, other):
        return (other.__class__ is self.__class__ and self.dn == other.dn and other.new_dn ==
                other.new_dn and to_dict_of_set(self.entry) == to_dict_of_set(other.entry))

    # - first rename, sorted by dn depth
    # - then update and creations, sorted by depth
    # - the deletions sorted by reverse of depth
    def __lt__(self, other):
        if self.order == other.order:
            n = len(str2dn(self.dn))
            m = len(str2dn(other.dn))
            if self.order == 4:  # Delete should be done from leaves to root
                return m < n
            else:
                return n < m  # Other operations must be donne from root to leaves
        else:
            return self.order < other.order

    def do(self, conn):
        pass

    def collect_result(self, conn):
        for msgid in self.msgids:
            try:
                self.results.append(conn.result2(msgid))
            except ldap.LDAPError, e:
                self.errors.append(e)

    def __str__(self):
        s = '%s %s' % (self.__class__.__name__, self.dn)
        if self.new_dn:
            s += ' to %s' % self.new_dn
        return s


class Create(Action):
    order = 3

    def do(self, conn):
        self.msgids.append(conn.add(self.dn, ldap.modlist.addModlist(self.entry)))


class Rename(Action):
    order = 1

    def do(self, conn):
        old_dn = str2dn(self.dn)
        new_dn = str2dn(self.new_dn)
        new_rdn = ldap.dn.dn2str(new_dn[:1])
        newsuperior = None
        if old_dn[1:] != new_dn[1:]:
            newsuperior = ldap.dn.dn2str(new_dn[1:])
        self.msgids.append(conn.rename(self.dn, new_rdn, newsuperior=newsuperior, delold=0))


class Update(Action):
    order = 2

    def do(self, conn):
        modlist = []
        for key, values in self.entry.iteritems():
            modlist.append((ldap.MOD_REPLACE, key, values))
        self.msgids.append(conn.modify(self.dn, modlist))


class Delete(Action):
    order = 4

    def do(self, conn):
        self.msgids.append(conn.delete(self.dn))


class Synchronize(object):
    '''Synchronize a source or records with an LDAP server'''
    BATCH_SIZE = 100

    # an iterable yield pair of (dn, attributes)
    source = None
    # an LDAP connection as provided by python-ldap
    target_conn = None

    # list or pairs, objectclass -> attribute
    pivot_attributes = []

    # attributes
    attributes = []

    # actions
    CREATE = 1
    UPDATE = 2
    RENAME = 3
    DELETE = 4

    all_filter = '(objectclass=*)'

    # actions
    actions = None
    case_insensitive_attribute = None

    def __init__(self, source, source_dn, target_conn, target_dn, attributes=None, all_filter=None,
                 pivot_attributes=None, logger=None, case_insensitive_attribute=None):
        self.source = source
        self.source_dn = source_dn
        self.target_conn = target_conn
        self.target_dn = target_dn
        self.attributes = list(set(istr(attribute) for attribute in attributes or self.attributes))
        self.all_filter = all_filter or self.all_filter
        self.pivot_attributes = pivot_attributes or self.pivot_attributes
        self.logger = logger or logging.getLogger(__name__)
        self.case_insensitive_attribute = map(istr, case_insensitive_attribute or self.case_insensitive_attribute or [])
        self.errors = []

    def massage_dn(self, old_dn):
        return old_dn[:-len(self.source_dn)] + self.target_dn

    def get_pivot_attribute(self, entry):
        '''Find a pivot attribute value for an LDAP entry'''
        for objc, attr in self.pivot_attributes:
            entry['objectclass'] = map(istr, entry['objectclass'])
            if objc in entry['objectclass']:
                try:
                    value = entry[attr]
                except KeyError:
                    raise Exception('entry missing pivot attribute %s: %s' % (attr, entry))
                break
        else:
            raise Exception('entry has unknown objectclasses %s' % entry['objectclass'])
        if len(value) != 1:
            raise Exception('entry pivot attribute %s must have only one value' % attr)
        if attr in self.case_insensitive_attribute:
            value = map(istr, value)
        return objc, attr, value[0]

    def get_target_entries(self, filterstr=None, attributes=[]):
        '''Return all target entries'''
        try:
            # Check base DN exist
            self.target_conn.search_s(self.target_dn, ldap.SCOPE_BASE)
            l = self.target_conn.paged_search_ext_s(self.target_dn, ldap.SCOPE_SUBTREE,
                                                filterstr=filterstr or self.all_filter,
                                                attrlist=attributes)
            return ((dn, idict(entry)) for dn, entry in l if dn)
        except ldap.NO_SUCH_OBJECT:
            return []

    def build_actions_for_entries(self, entries):
        seen_dn = self.seen_dn
        renamed_dn = self.renamed_dn
        in_dns = []
        out_filters = []
        # Transform input entries into filters
        for dn, entry in entries:
            objectclass, attr, value = self.get_pivot_attribute(entry)
            in_dns.append(((attr, value), (dn, entry)))
            filter_tpl = '(&(objectclass=%%s)(%s=%%s))' % attr
            out_filters.append(
                filter_format(filter_tpl, (objectclass, value)))
        out_filter = '(|%s)' % ''.join(out_filters)
        # Get existing output entries
        out_dns = {}
        for dn, entry in self.get_target_entries(filterstr=out_filter, attributes=self.attributes):
            objectclass, attr, value = self.get_pivot_attribute(entry)
            out_dns[(attr, value)] = dn, entry
        for pivot, (source_dn, entry) in in_dns:
            target_dn = self.massage_dn(source_dn)
            seen_dn.add(target_dn)
            if pivot in out_dns:
                out_dn, out_entry = out_dns[pivot]
                # translate dn to dn after all previous renames
                out_ava = str2dn(out_dn)
                rename = True
                while rename:
                    rename = False
                    for i in range(len(out_ava) - 1, 0, -1):
                        if out_ava[i:] in renamed_dn:
                            # rewrite suffix if it has been renamed
                            out_ava = out_ava[:i] + renamed_dn[out_ava[i:]]
                            rename = True
                            break
                new_out_dn = ldap.dn.dn2str(out_ava)
                if new_out_dn != target_dn:
                    seen_dn.add(out_dn)
                    self.rename(new_out_dn, target_dn)
                    renamed_dn[str2dn(new_out_dn)] = str2dn(target_dn)
                if to_dict_of_set(out_entry) != to_dict_of_set(entry):
                    new_entry = {}
                    for attribute in self.attributes:
                        if attribute in to_dict_of_set(entry):
                            new_entry[attribute] = entry[attribute]
                        if attribute in to_dict_of_set(out_entry) and not to_dict_of_set(entry).get(attribute):
			    new_entry[attribute] = []
                    self.update(target_dn, new_entry)
            else:
                self.create(target_dn, entry)

    def build_actions(self):
        self.seen_dn = set()
        self.renamed_dn = {}
        self.actions = []
        # Order source entries by DN depth
        entries = list(self.source)
        entries.sort(key=lambda (dn, entry): len(str2dn(dn)))
        for dn, entry in entries:
            for key in entry.keys():
                if not key in self.attributes:
                    del entry[key]
        # First create, rename and update
        for batch in batch_generator(entries, self.BATCH_SIZE):
            self.build_actions_for_entries(batch)
        # Then delete
        for dn, entry in self.get_target_entries(filterstr=self.get_pivot_filter()):
            if dn not in self.seen_dn:
                self.delete(dn)
        # Now sort actions by their special order
        self.actions.sort()

    def get_pivot_filter(self):
        filter_tpl = '(objectclass=%s)'
        filters = [filter_format(filter_tpl, (objc,)) for objc, attr in self.pivot_attributes]
        return '(|%s)' % ''.join(filters)

    def create(self, dn, entry):
        self.actions.append(Create(dn=dn, entry=entry))

    def rename(self, old_dn, new_dn):
        self.actions.append(Rename(dn=old_dn, new_dn=new_dn))

    def update(self, dn, entry):
        self.actions.append(Update(dn=dn, entry=entry))

    def delete(self, dn):
        self.actions.append(Delete(dn=dn))

    def apply_actions(self):
        '''Apply actions, wait for result of different kind of actions
           separately, since openldap seem to reorder some of them'''

        def action_key(action):
            return (action.__class__, str2dn(action.dn))
        for key, sequence in groupby(self.actions, action_key):
            for batch in batch_generator(sequence, self.BATCH_SIZE):
                for action in batch:
                    action.do(self.target_conn)
                    self.logger.debug('applying %s', action)
                self.logger.debug('waiting for completion of %d actions', len(batch))
                for action in batch:
                    action.collect_result(self.target_conn)

    def run(self):
        self.build_actions()
        self.apply_actions()
