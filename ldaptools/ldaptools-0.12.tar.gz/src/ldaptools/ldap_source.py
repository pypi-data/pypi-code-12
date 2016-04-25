import ldap

from ldaptools.utils import idict, istr


class LDAPSource(object):
    entries = None
    conn = None
    base_dn = None
    filterstr = '(objectclass=*)'
    attributes = None

    def __init__(self, conn, base_dn=None, filterstr=None, attributes=None):
        assert conn
        self.conn = conn or self.conn
        self.filterstr = filterstr or self.filterstr
        self.attributes = attributes or self.attributes
        self.base_dn = base_dn or self.base_dn

    def search(self):
        for dn, entry in self.conn.paged_search_ext_s(self.base_dn, ldap.SCOPE_SUBTREE,
                                                      filterstr=self.filterstr,
                                                      attrlist=self.attributes):
            if not dn:
                continue
            entry = idict(entry)
            if 'objectclass' in entry:
                entry['objectclass'] = [istr(v) for v in entry['objectclass']]
            yield dn, entry

    def __iter__(self):
        return self.search()
