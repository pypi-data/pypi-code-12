#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright (c) 2014 uralbash <root@uralbash.ru>
# Copyright (c) 2016 procool <ya.procool@ya.ru>
#
# Distributed under terms of the MIT license.
from sqlalchemy.orm import mapper

from .events import TreesManager
from .mixins import AnotherSAMPTT, DjangoSAMPTT

__mixins__ = [AnotherSAMPTT, DjangoSAMPTT]
__all__ = ['AnotherSAMPTT', 'DjangoSAMPTT', 'mptt_sessionmaker']

def register_manager(cls_):
    tree_manager = TreesManager(cls_)
    tree_manager.register_mapper(mapper)
    mptt_sessionmaker = tree_manager.register_factory
    return tree_manager, mptt_sessionmaker

## tree_manager, mptt_sessionmaker = register_manager(AnotherSAMPTT)
