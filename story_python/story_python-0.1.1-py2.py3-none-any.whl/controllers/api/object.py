#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier

import story

class ObjectApiController(appier.Controller):

    @appier.route("/api/objects", "GET", json = True)
    @appier.ensure(token = "admin")
    def list(self):
        object = appier.get_object(alias = True, find = True)
        objects = story.Object.find(map = True, **object)
        return objects
