import aioxmpp.xso as xso

from aioxmpp.utils import namespaces

namespaces.xep0131_shim = "http://jabber.org/protocol/shim"


class Header(xso.XSO):
    TAG = (namespaces.xep0131_shim, "header")
