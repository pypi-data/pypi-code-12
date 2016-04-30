# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 08:28:25 2013

@author: mel
"""


import model


class Member(model.TComponent):
    """Implements member"""
    def __init__(self, **kwargs):
        "Initialization"
        super(Member, self).__init__(**kwargs)
        topClass = self.outer_class
        topClass._lastSrcTime = None
        topClass._lastHdrTime = None

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        return super(Member, self).get_kwargs()

