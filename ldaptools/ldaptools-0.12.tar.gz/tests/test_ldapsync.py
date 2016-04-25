import pytest
import ldap

from ldaptools.ldapsync.cmd import main



def test_ldapsync_ldif_to_ldapi(slapd, ldif_path, attributes, pivot_attributes):
    args = [
        '--source-uri', ldif_path,
        '--source-base-dn', 'dc=orga2',
        '--target-uri', slapd.ldap_url,
        '--target-base-dn', 'o=orga',
        '--attributes', ' '.join(attributes),
        '--verbose',
    ]
    for object_class, pivot_attribute in pivot_attributes:
        args += ['--object-class-pivot', '%s %s' % (object_class, pivot_attribute)]
    main(args)
    main(args)
    conn = slapd.get_connection()
    assert len(conn.search_s('o=orga', ldap.SCOPE_SUBTREE)) == 2
    assert set([dn for dn, entry in conn.search_s('o=orga', ldap.SCOPE_SUBTREE)]) == set(['o=orga',
                                                                                          'uid=admin,o=orga'])


def test_ldapsync_ldif_to_ldapi_attributes_file(slapd, ldif_path, attributes_path, pivot_attributes):
    args = [
        '--source-uri', ldif_path,
        '--source-base-dn', 'dc=orga2',
        '--target-uri', slapd.ldap_url,
        '--target-base-dn', 'o=orga',
        '--attributes-file', attributes_path,
        '--verbose',
    ]
    for object_class, pivot_attribute in pivot_attributes:
        args += ['--object-class-pivot', '%s %s' % (object_class, pivot_attribute)]
    main(args)
    main(args)
    conn = slapd.get_connection()
    assert len(conn.search_s('o=orga', ldap.SCOPE_SUBTREE)) == 2
    assert set([dn for dn, entry in conn.search_s('o=orga', ldap.SCOPE_SUBTREE)]) == set(['o=orga',
                                                                                          'uid=admin,o=orga'])


def test_ldapsync_ldap_to_ldap(slapd_tcp1, slapd_tcp2, ldif, attributes, pivot_attributes):
    slapd_tcp1.add_db('dc=orga2')
    slapd_tcp1.add_ldif(ldif)

    args = [
        '--source-uri', slapd_tcp1.ldap_url,
        '--source-bind-dn', slapd_tcp1.root_bind_dn,
        '--source-bind-password', slapd_tcp1.root_bind_password,
        '--source-base-dn', 'dc=orga2',

        '--target-uri', slapd_tcp2.ldap_url,
        '--target-bind-dn', slapd_tcp2.root_bind_dn,
        '--target-bind-password', slapd_tcp2.root_bind_password,
        '--target-base-dn', 'o=orga',
        '--attributes', ' '.join(attributes),
        '--verbose',
    ]
    for object_class, pivot_attribute in pivot_attributes:
        args += ['--object-class-pivot', '%s %s' % (object_class, pivot_attribute)]
    main(args)
    main(args)
    conn = slapd_tcp2.get_connection()
    assert len(conn.search_s('o=orga', ldap.SCOPE_SUBTREE)) == 2
    assert set([dn for dn, entry in conn.search_s('o=orga', ldap.SCOPE_SUBTREE)]) == set(['o=orga',
                                                                                          'uid=admin,o=orga'])
