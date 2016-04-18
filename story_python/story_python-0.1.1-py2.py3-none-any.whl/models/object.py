#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier

from . import base

class Object(base.StoryBase):

    key = dict(
        index = True,
        safe = True,
        immutable = True
    )

    name = dict(
        index = True
    )

    engine = dict(
        index = True,
        safe = True
    )

    file = appier.field(
        type = appier.File,
        private = True
    )

    bucket = appier.field(
        type = appier.references(
            "Bucket",
            name = "id"
        )
    )

    @classmethod
    def validate(cls):
        return super(Object, cls).validate() + [
            appier.not_null("name"),
            appier.not_empty("name")
        ]

    def pre_create(self):
        base.StoryBase.pre_create(self)
        self.key = self.secret()
        self.description = self.key[:8]
