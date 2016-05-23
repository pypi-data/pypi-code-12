import StringIO

from ldaptools.ldif_utils import ListLDIFParser

def test_ldifparser():
    parser = ListLDIFParser(StringIO.StringIO('''dn: o=orga
objectClass: organization'''))
    parser.parse()
    assert len(list(parser)) == 1
    assert list(parser)[0][0] == 'o=orga'
    assert list(parser)[0][1] == {'objectClass': ['organization']}
