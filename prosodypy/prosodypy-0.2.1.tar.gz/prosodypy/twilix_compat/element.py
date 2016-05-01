from copy import copy

from prosodypy import lua

from twisted.words.xish.xmlstream import XmlStream

class FakeStream(XmlStream):
    def __init__(self, stream_xmlns='jabber:client', *args, **kwargs):
        XmlStream.__init__(self, *args, **kwargs)
        self.connectionMade()
        self.dataReceived('<stream xmlns="%s">' % (stream_xmlns,))
        self.resulted_element = None

    def dispatch(self, element, event=None):
        if event is not None:
            return
        self.resulted_element = element

xmlstream = FakeStream()

def parse_string(stanza):
    xmlstream.dataReceived(stanza.encode('utf-8'))
    result = xmlstream.resulted_element
    assert result is not None
    xmlstream.resulted_element = None
    return result

def parse_prosody_stanza(stanza):
    assert lua is not None
    return parse_string(lua.eval('tostring(...)', stanza))

if lua:
    Stanza = lua.require("util.stanza").stanza
def build_prosody_stanza(element, current_ns=None, current_tag=None):
    name = element.name
    attrs = copy(element.attributes)
    if element.uri != current_ns:
        attrs['xmlns'] = element.uri
        current_ns = element.uri
    added_tag = False
    if current_tag is None:
        current_tag = Stanza(name, lua.table_from(attrs))
    else:
        current_tag.tag(current_tag, name, lua.table_from(attrs))
        added_tag = True
    for child in element.children:
        if isinstance(child, unicode):
            current_tag.text(current_tag, child)
        else:
            build_prosody_stanza(child, current_ns, current_tag)
    if added_tag:
        current_tag.up(current_tag)
    return current_tag
