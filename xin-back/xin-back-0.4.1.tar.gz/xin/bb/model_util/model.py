from mongoengine import Document

from xin.bb.model_util.version import HistorizedDocument
from xin.bb.model_util.searcher import SearchableDocument
from xin.bb.model_util.controller import ControlledDocument


class Marshallable(Document):

    """
    Special unmarshal to properly handle properties
    """
    meta = {'abstract': True}

    class Marshaller:

        def __init__(self, doc):
            self.doc = doc

        def __getitem__(self, key):
            return getattr(self.doc, key)

    def __marshallable__(self):
        return self.Marshaller(self)


class BaseDocument(ControlledDocument, Marshallable, HistorizedDocument,
                   SearchableDocument):

    """
    Document default class, all actual documents should inherit from this one
    """
    meta = {'abstract': True}
