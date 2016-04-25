import pytest
import tempfile
import os

from ldaptools.slapd import Slapd


@pytest.fixture
def slapd(request):
    return Slapd(ldap_url=getattr(request, 'param', None))


@pytest.fixture
def slapd_tcp1(request):
    return Slapd(ldap_url='ldap://localhost:3389')


@pytest.fixture
def slapd_tcp2(request):
    return Slapd(ldap_url='ldap://localhost:4389')


@pytest.fixture
def ldif():
    return '''dn: dc=orga2
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


@pytest.fixture
def attributes():
    return ['o', 'objectClass', 'uid', 'sn', 'givenName', 'mail', 'dc', 'cn']


@pytest.fixture
def pivot_attributes():
    return (
        ('organization', 'o'),
        ('inetOrgPerson', 'uid'),
    )


@pytest.fixture
def ldif_path(request, ldif):
    handle, path = tempfile.mkstemp()
    with open(path, 'w') as f:
        f.write(ldif)
        f.flush()
    def finalize():
        os.unlink(path)
    request.addfinalizer(finalize)
    return path


@pytest.fixture
def attributes_path(request, attributes):
    handle, path = tempfile.mkstemp()
    with open(path, 'w') as f:
        for attribute in attributes:
            print >>f, ' %s ' % attribute
        f.flush()
    def finalize():
        os.unlink(path)
    request.addfinalizer(finalize)
    return path
