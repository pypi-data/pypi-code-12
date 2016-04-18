#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier

from . import base

class Bucket(base.StoryBase):

    key = dict(
        index = True,
        safe = True,
        immutable = True
    )

    name = dict(
        index = True
    )

    @classmethod
    def validate(cls):
        return super(Bucket, cls).validate() + [
            appier.not_null("name"),
            appier.not_empty("name")
        ]

    def pre_create(self):
        base.StoryBase.pre_create(self)
        self.key = self.secret()
        self.description = self.key[:8]
