# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import uuid
import app
from ctx import theContext as context
import model
import tran


class TComponent(model.TCommon, tran.TransactionObject):
    """We need to be able to deal with several kinds of TransactionObject.
    For example, with TransactionFSObject now and with TransactionDBObject in a near future.
    For this reason we need to split the data management and transaction management."""
    def __init__(self, **kwargs):
        """init"""
        super(TComponent, self).__init__(**kwargs)


