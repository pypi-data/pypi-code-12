# -*- coding: UTF-8 -*-
# lvjiyong on 2015/4/19.
from enum import Enum


class Pack(Enum):
    """内容存储片断Key"""
    title = 'title'
    html = 'html'
    text = 'text'
    header = 'header'
    body = "body"
    exact_title = 'exact_title'


class Node(Enum):
    """节点名"""
    title = 'title'
    head = 'head'
    body = 'body'


class ItemProp(Enum):
    """ItemProp名"""
    author = 'author'
    name = 'name'
    itemprop = 'itemprop'