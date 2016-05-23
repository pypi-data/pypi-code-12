import StringIO

import ldap

from ldaptools.synchronize import Synchronize, Delete, Rename, Update, Create 
from ldaptools.ldif_utils import ListLDIFParser
from ldaptools.ldap_source import LDAPSource


def test_synchronize_ldif(slapd):
    pivot_attributes = (
        ('organization', 'o'),
        ('inetOrgPerson', 'uid'),
        ('organizationalUnit', 'ou'),
    )
    attributes = ['o', 'objectClass', 'uid', 'sn', 'givenName', 'mail', 'dc', 'cn']
    conn = slapd.get_connection_admin()

    def syn_ldif(ldif):
        parser = ListLDIFParser(StringIO.StringIO(ldif))
        parser.parse()
        synchronize = Synchronize(parser, 'o=orga', conn, 'o=orga',
                                  pivot_attributes=pivot_attributes,
                                  attributes=attributes)
        synchronize.run()
        return synchronize

    ldif = '''dn: o=orga
o: orga
dc: coucou
objectClass: organization
objectClass: dcObject

dn: uid=admin,o=orga
objectClass: inetOrgPerson
cn: John Doe
uid: admin
sn: John
givenName: Doe
mail: john.doe@entrouvert.com'''

    synchronize = syn_ldif(ldif)
    assert all(not action.errors for action in synchronize.actions)
    assert len(synchronize.actions) == 2
    assert len(conn.search_s('o=orga', ldap.SCOPE_SUBTREE)) == 2

    # Rename 
    slapd.add_ldif('''dn: ou=people,o=orga
ou: people
objectClass: organizationalUnit''')
    conn.rename_s('uid=admin,o=orga', 'cn=John Doe', newsuperior='ou=people,o=orga', delold=0)
    assert set([dn for dn, entry in conn.search_s('o=orga', ldap.SCOPE_SUBTREE)]) == set(['o=orga',
                                                                                          'ou=people,o=orga',
                                                                                          'cn=John Doe,ou=people,o=orga'])
    synchronize.run()

    assert not any([action.errors for action in synchronize.actions])
    assert len(synchronize.actions) == 2
    assert isinstance(synchronize.actions[0], Rename)
    assert isinstance(synchronize.actions[1], Delete)
    assert len(conn.search_s('o=orga', ldap.SCOPE_SUBTREE)) == 2
    assert set([dn for dn, entry in conn.search_s('o=orga', ldap.SCOPE_SUBTREE)]) == set(['o=orga',
                                                                                          'uid=admin,o=orga'])

    # Delete one entry
    ldif = '''dn: o=orga
o: orga
dc: coucou
objectClass: organization
objectClass: dcobject
'''
    synchronize = syn_ldif(ldif)
    assert all(not action.errors for action in synchronize.actions)
    assert len(synchronize.actions) == 1
    assert len(conn.search_s('o=orga', ldap.SCOPE_SUBTREE)) == 1


def test_synchronize_ldap(slapd):
    pivot_attributes = (
        ('organization', 'o'),
        ('inetOrgPerson', 'uid'),
        ('organizationalUnit', 'ou'),
    )
    attributes = ['o', 'objectClass', 'uid', 'sn', 'givenName', 'mail', 'dc', 'cn']
    conn = slapd.get_connection_admin()

    slapd.add_db('dc=orga2')
    ldif = '''dn: dc=orga2
o: orga
dc: orga2
objectClass: organization
objectClass: dcObject

dn: uid=admin,dc=orga2
objectClass: inetOrgPerson
cn: John Doe
uid: admin
sn: John
givenName: Doe
mail: john.doe@entrouvert.com'''
    slapd.add_ldif(ldif)

    source = LDAPSource(conn, base_dn='dc=orga2', attributes=attributes)


    synchronize = Synchronize(source, 'dc=orga2', conn, 'o=orga',
                              pivot_attributes=pivot_attributes,
                              attributes=attributes)
    synchronize.run()

    assert all(not action.errors for action in synchronize.actions)
    assert len(synchronize.actions) == 2
    assert isinstance(synchronize.actions[0], Update)
    assert isinstance(synchronize.actions[1], Create)
    assert len(conn.search_s('o=orga', ldap.SCOPE_SUBTREE)) == 2
    assert set([dn for dn, entry in conn.search_s('o=orga', ldap.SCOPE_SUBTREE)]) == set(['o=orga',
                                                                                          'uid=admin,o=orga'])

    # Rename 
    slapd.add_ldif('''dn: ou=people,o=orga
ou: people
objectClass: organizationalUnit''')
    conn.rename_s('uid=admin,o=orga', 'cn=John Doe', newsuperior='ou=people,o=orga', delold=0)
    assert set([dn for dn, entry in conn.search_s('o=orga', ldap.SCOPE_SUBTREE)]) == set(['o=orga',
                                                                                          'ou=people,o=orga',
                                                                                          'cn=John Doe,ou=people,o=orga'])
    synchronize.run()

    assert not any([action.errors for action in synchronize.actions])
    assert len(synchronize.actions) == 2
    assert isinstance(synchronize.actions[0], Rename)
    assert isinstance(synchronize.actions[1], Delete)
    assert len(conn.search_s('o=orga', ldap.SCOPE_SUBTREE)) == 2
    assert set([dn for dn, entry in conn.search_s('o=orga', ldap.SCOPE_SUBTREE)]) == set(['o=orga',
                                                                                          'uid=admin,o=orga'])

    # Delete one entry
    conn.delete_s('uid=admin,dc=orga2')
    synchronize.run()

    assert all(not action.errors for action in synchronize.actions)
    assert len(synchronize.actions) == 1
    assert isinstance(synchronize.actions[0], Delete)
    assert len(conn.search_s('o=orga', ldap.SCOPE_SUBTREE)) == 1

def test_synchronize_deep_rename(slapd):
    pivot_attributes = (
        ('organization', 'o'),
        ('inetOrgPerson', 'uid'),
        ('organizationalUnit', 'ou'),
    )
    attributes = ['o', 'objectClass', 'uid', 'sn', 'givenName', 'mail', 'dc',
                  'cn', 'description', 'ou']
    conn = slapd.get_connection_admin()

    def syn_ldif(ldif):
        parser = ListLDIFParser(StringIO.StringIO(ldif))
        parser.parse()
        synchronize = Synchronize(parser, 'o=orga', conn, 'o=orga',
                                  pivot_attributes=pivot_attributes,
                                  attributes=attributes)
        synchronize.run()
        return synchronize

    ldif = '''dn: o=orga
o: orga
dc: coucou
objectClass: organization
objectClass: dcObject

dn: ou=people,o=orga
objectClass: organizationalUnit
ou: people
description: coin

dn: uid=admin,ou=people,o=orga
objectClass: inetOrgPerson
cn: John Doe
uid: admin
sn: John
givenName: Doe
mail: john.doe@entrouvert.com'''

    synchronize = syn_ldif(ldif)
    assert all(not action.errors for action in synchronize.actions)
    assert len(synchronize.actions) == 3
    assert len(conn.search_s('o=orga', ldap.SCOPE_SUBTREE)) == 3

    # Rename 
    ldif = '''dn: o=orga
o: orga
dc: coucou
objectClass: organization
objectClass: dcObject

dn: description=coin,o=orga
objectClass: organizationalUnit
ou: people
description: coin

dn: cn=John Doe,description=coin,o=orga
objectClass: inetOrgPerson
cn: John Doe
uid: admin
sn: John
givenName: Doe
mail: john.doe@entrouvert.com'''

    synchronize = syn_ldif(ldif)

    assert all(not action.errors for action in synchronize.actions)
    assert len(synchronize.actions) == 2
    assert len(conn.search_s('o=orga', ldap.SCOPE_SUBTREE)) == 3
