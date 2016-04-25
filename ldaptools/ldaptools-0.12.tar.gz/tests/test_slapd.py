import pytest

import ldap


@pytest.mark.parametrize('slapd', [None, 'ldap://localhost:1389'], indirect=True)
def test_checkpoint(slapd):
    conn = slapd.get_connection()
    conn.simple_bind_s('uid=admin,cn=config', 'admin')
    assert conn.whoami_s() == 'dn:uid=admin,cn=config'
    slapd.stop()
    slapd.checkpoint()
    slapd.start()
    slapd.add_ldif('''dn: uid=admin,o=orga
objectclass: person
objectclass: uidObject
uid:in
cn: n
sn: n
''')
    conn = slapd.get_connection()
    assert len(conn.search_s('o=orga', ldap.SCOPE_SUBTREE)) == 2
    slapd.stop()
    slapd.restore()
    slapd.start()
    conn = slapd.get_connection()
    assert len(conn.search_s('o=orga', ldap.SCOPE_SUBTREE)) == 1
