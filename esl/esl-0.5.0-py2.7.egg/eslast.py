# @Author: BingWu Yang <detailyang>
# @Date:   2016-03-30T17:00:32+08:00
# @Email:  detailyang@gmail.com
# @Last modified by:   detailyang
# @Last modified time: 2016-04-10T16:17:55+08:00
# @License: The MIT License (MIT)


import re


keypattern = re.compile('--[qhb](.*)')


class ESLNode(object):
    """ Abstract base class for AST nodes.
    """
    def children(self):
        pass


class RequestNode(ESLNode):
    def __init__(self, method, left, right):
        self.method =method
        self.left = left
        self.right = right

    def children(self):
        nodelist = []
        if self.left is not None:
                nodelist.append(("left", self.left))
        if self.right is not None:
                nodelist.append(("right", self.right))
        return tuple(nodelist)


class MethodNode(ESLNode):
    def __init__(self, method):
        self.name = method.upper() or 'GET'


class URLNode(ESLNode):
    def __init__(self, url):
        self.url = url


class HeaderNode(ESLNode):
    def __init__(self, header):
        r = keypattern.match(header)
        self.key = r.group(1)

class QueryStringNode(ESLNode):
    def __init__(self, qs):
        r = keypattern.match(qs)
        self.key = r.group(1)


class BodyNode(ESLNode):
    def __init__(self, body):
        r = keypattern.match(body)
        self.key = r.group(1)


class ValueNode(ESLNode):
    def __init__(self, value):
        self.value = value[1:] if value.startswith('=') else value


class ShellNode(ESLNode):
    def __init__(self, value):
        self.value = value[3:-1] if value.startswith('=$(') and value.endswith(')') else value


class OptionListNode(ESLNode):
    def __init__(self, options):
        self.options = options or []

    def children(self):
        nodelist = []
        for i, child in enumerate(self.options or []):
            nodelist.append(('options[%d]' % i, child))
        return tuple(nodelist)

    def append(self, option):
        self.options.append(option)
        return self


class OptionNode(ESLNode):
    def __init__(self, key, value):
        self.key = key
        self.value = value
