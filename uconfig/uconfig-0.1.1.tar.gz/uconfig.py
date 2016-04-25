#!/usr/env/bin python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function
import sys
import os
import glob

"""
    uconfig
    =======

    uconfig is a simple parser for unix style configurations.

    Example configuration syntax:
    -----------------------------

    node1 {
        field1 value;

        node2 {
            field2 value;
        }
    }

    License:
    --------

    Copyright (c) 2016, David Ewelt
    All rights reserved.

    Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

__author__  = "David Ewelt"
__version__ = "0.1.1"
__license__ = "BSD"

from io import StringIO

if sys.version_info > (3,):
    long = int

TOKEN_ADD_VALUE                = ";"
TOKEN_OPEN_NODE                = "{"
TOKEN_CLOSE_NODE               = "}"
TOKEN_SET_BASE                 = ":"
TOKEN_SINGLELINE_COMMENT_START = "//"
TOKEN_SINGLELINE_COMMENT_END   = "\n"
TOKEN_MULTILINE_COMMENT_START  = "/*"
TOKEN_MULTILINE_COMMENT_END    = "*/"
TOKEN_EOF                      = "<EOF>"

class IOUtil(object):
    @staticmethod
    def unquote(inp):
        quot = None
        if inp.startswith("'"):
            quot = "'"
        elif inp.startswith('"'):
            quot = '"'
        else:
            return inp
        if inp.endswith(quot):
            return inp[1:-1]
        return inp

    @staticmethod
    def split_str_escaped(inp, sep, max_split=0):
        fp = StringIO(inp)

        result = []

        n = 0
        while True:
            if max_split > 0 and n == max_split:
                rest = fp.read()
                if len(rest) > 0:
                    result.append(rest)
                return result

            t, p = IOUtil.read_until(fp, sep)
            result.append(p)

            if t == TOKEN_EOF:
                break
            n += 1

        return result

    @staticmethod
    def read_until(fp, tokens=[]):
        buf = ""
        cbuf = ""

        instr = False
        instr_token = None

        comment = False
        line_comment = False
        multiline_comment = False

        while True:
            c = fp.read(1)
            if len(c) == 0:
                break

            #-- comments
            if not instr:
                if not comment:
                    if buf.endswith(TOKEN_SINGLELINE_COMMENT_START):
                        comment = True
                        line_comment = True
                        cbuf = ""
                        buf = buf[:-len(TOKEN_SINGLELINE_COMMENT_START)]
                        continue
                    elif buf.endswith(TOKEN_MULTILINE_COMMENT_START):
                        comment = True
                        multiline_comment = True
                        cbuf = ""
                        buf = buf[:-len(TOKEN_MULTILINE_COMMENT_START)]
                        continue
                elif line_comment:
                    if cbuf.endswith(TOKEN_SINGLELINE_COMMENT_END):
                        comment = False
                        line_comment = False
                        continue
                elif multiline_comment:
                    if cbuf.endswith(TOKEN_MULTILINE_COMMENT_END):
                        cbuf = cbuf[:-len(TOKEN_MULTILINE_COMMENT_END)]
                        comment = False
                        multiline_comment = False
                        continue

            if comment:
                cbuf += c
                continue

            if c in "\t\r\n":
                continue

            #-- collect data
            buf += c

            #-- string escaping
            if instr:
                if c == instr_token: #-- end only with the same token with wich it starts
                    instr = False
                    continue
            else:
                if c in ("'",'"'):
                    instr = True
                    instr_token = c
                    continue

            #-- collect data
            #buf += c

            #-- test for token
            if not instr:
                for t in tokens:
                    if buf.endswith(t):
                        buf = buf[:-len(t)]
                        token = t
                        break
                else:
                    token = None

                #-- if token yield result
                if not token is None:
                    return token, buf.strip()


        return TOKEN_EOF, buf

    @staticmethod
    def parse(fp, level=0):
        sequence = []
        while True:
            token, data = IOUtil.read_until(fp, (TOKEN_ADD_VALUE, TOKEN_OPEN_NODE, TOKEN_CLOSE_NODE))
            if token == TOKEN_EOF:
                if level > 0:
                    raise ParseError("unexpected EOF")
                break

            if token == TOKEN_ADD_VALUE:
                sequence.append(data)
            elif token == TOKEN_OPEN_NODE:
                sequence.append( (data, IOUtil.parse(fp, level+1)) )
            elif token in TOKEN_CLOSE_NODE:
                break

        return sequence

class ParseError(Exception):
    pass

class NodeBase(object):
    """
        The Base Node
    """

    def _on_add_value(self, value):
        return True

    def _on_open_node(self, name, body):
        return True

    def _parse(self, seq):
        for e in seq:
            if isinstance(e, tuple):
                self._on_open_node(*e)
            else:
                self._on_add_value(e)

    def read(self, fp):
        seq = IOUtil.parse(fp, level=0)
        self._parse(seq)

class Node(NodeBase):
    """
        Simplest possible parser
    """

    def __init__(self, name="", parent=None):
        self.name = name
        self.parent = parent
        self._node_type = type(self)
        self._values = []
        self._nodes = []

    def get_root(self):
        if self.parent is None:
            return self
        return self.parent.get_root()

    def get_dict(self):
        return {
            "name": self.name,
            "values": self._values,
            "nodes": [ n.get_dict() for n in self._nodes ]
        }

    def _create_instance(self, *args, **kwargs):
        """
            @rtype: Node
        """
        return self._node_type(*args, **kwargs)

    def clone(self):
        clone = self._create_instance(self.name, self.parent)
        clone._values = list(self._values)
        for n in self._nodes:
            clone._nodes.append(n.clone())
        return clone

    def _on_add_value(self, value):
        self._values.append( value )
        return True

    def _on_open_node(self, name, body):
        node = self._create_instance(name, parent=self)
        node._parse(body)
        self._nodes.append(node)
        return True

class SimpleNode(Node):
    """
        Simple representation with multiple names allowed

        field1;
        node1 {
            field1;
        }
        field1;

        becomes:

        Node(
            values[
                "field1"
                "field1"
            ]
            nodes[
                Node(
                    values[
                        "field1"
                    ]
                    nodes[]
                )
            ]
        )
    """
    def __init__(self, name="", parent=None):
        Node.__init__(self, name, parent)

    def _on_add_value(self, value):
        if len(value) == 0:
            return False
        return Node._on_add_value(self, value)

    def _on_open_node(self, name, body):
        if len(name) == 0:
            raise ParseError("empty node name")
        return Node._on_open_node(self, name, body)

    def _pprint(self, level=0, indentation="   "):
        o = indentation*level + self.name
        if len(self.name) > 0:
            o += " "
        o += "{"
        if len(self._values) > 0 or len(self._nodes) > 0:
            o += "\n"
        for v in self._values:
            o += indentation*(level+1) + v + ";\n"
        for n in self._nodes:
            o += n._pprint(level+1, indentation)
        o += indentation*level + "}\n"
        return o

    def pprint(self, indentation="   "):
        print( self._pprint(0, indentation) )

    def get_node(self, name):
        for n in self._nodes:
            if n.name == name:
                return n

    def get_nodes(self, name):
        for n in self._nodes:
            if n.name == name:
                yield n

    def __getitem__(self, key):
        """
            @rtype: SimpleNode
        """
        if isinstance(key, str):
            return self.get_node(key)
        if isinstance(key, tuple) or isinstance(key, list): #-- if ("name", index) is given as key
            n,i = key
            return list(self.get_nodes(n))[i]

class NameValueNode(Node):
    """
        Like SimpleNode but nodes can have names and fields are expected to define a name-value pair.

        field1 value;
        node1 {
            field2;
        }

        becomes:

        NameValueNode(
            values {
                "field1": "value"
            }
            nodes {
                "node1": NameValueNode(
                    values {
                        "field2": None
                    }
                )
            }
        )
    """
    def __init__(self, name="", parent=None):
        Node.__init__(self, name, parent)
        self._values = {}
        self._nodes = {}

    def clone(self):
        clone = self._create_instance(self.name, self.parent)
        clone._values = dict(self._values)
        for k,v in self._nodes.items():
            clone._nodes[k] = v.clone()
        return clone

    def get_dict(self):
        return self.name, {
            "values": self._values,
            "nodes": dict([ i.get_dict() for i in self._nodes.values() ])
        }

    def inherit(self, node):
        """
            @type node: NameValueNode
        """
        if node is None:
            return
        node = node.clone()
        self._values.update(node._values)
        self._nodes.update(node._nodes)

    def _on_add_value(self, value):
        if len(value) == 0:
            return False

        v = IOUtil.split_str_escaped(value, " ", 1)
        if len(v) > 1:
            name, value = v[0].strip(), IOUtil.unquote( v[1].strip() )
        else:
            name, value = value, None

        if not value is None:
            value = value.decode('string_escape')

        if name == "include":
            config_file = os.path.abspath( self.get_root().file )
            config_path,_ = os.path.split(config_file)

            if not os.path.isabs(value):
                value = os.path.join(config_path, value)

            for p in glob.glob(value):
                p = os.path.abspath( p )

                if not os.path.isfile(p):
                    continue

                if p == config_file: #-- dont include self
                    continue

                with open(p, "rb") as fp:
                    self.read(fp)

            return True

        self._values[name] = value

        return True

    def _on_open_node(self, name, body):
        if len(name) == 0:
            raise ParseError("empty node name")

        node = self._create_instance(name, parent=self)
        self._nodes[name] = node
        node._parse(body)

        return True

    #-- value handling

    def has_value(self, name):
        return name in self._values

    def get_value(self, name, default=None):
        if not name in self._values:
            return default
        v = self._values[name]
        if v is None:
            return default
        return v

    def set_value(self, name, value):
        self._values[name] = value

    def get_list(self, name, default=[], seperator=" "):
        if not self.has_value(name):
            return default
        return [ IOUtil.unquote(i) for i in IOUtil.split_str_escaped(self.get_value(name, default), seperator) ]

    def get_int(self, name, default=0):
        if not self.has_value(name):
            return default
        return int(self.get_value(name, default))

    def get_long(self, name, default=0):
        if not self.has_value(name):
            return default
        return long(self.get_value(name, default))

    def get_float(self, name, default=0.0):
        if not self.has_value(name):
            return default
        return float(self.get_value(name, default))

    def get_bool(self, name, default=False):
        if not self.has_value(name):
            return default

        v = self.get_value(name, default).lower()
        if v == "true":
            return True
        if v == "false":
            return False

        return bool(v)

    #-- node handling

    def get_node(self, name):
        return self._nodes[name]

    def get(self, path):
        if path[0] == "@":
            path = path[1:]
            return self.get_root().get(path)

        if "." in path:
            sub, rest = path.split(".",1)
            return self.get_node(sub).get(rest)
        elif "<" in path:
            sub, rest = path.split("<",1)
            return self.parent.get(rest)
        elif "#" in path:
            sub, rest = path.split("#",1)
            if len(sub) > 0:
                return self.get_node(sub).get("#"+rest)
            return self.get_value(rest)
        else:
            return self.get_node(path)

    def set(self, path, value, create_nodes=False):
        if path[0] == "@":
            path = path[1:]
            return self.get_root().get(path)

        if "." in path:
            sub, rest = path.split(".",1)
            if not sub in self._nodes and create_nodes:
                self._nodes[sub] = self._create_instance(sub, parent=self)
            return self._nodes[sub].set(rest, value, create_nodes)
        elif "#" in path:
            sub, rest = path.split("#",1)
            if len(sub) > 0:
                if not sub in self._nodes and create_nodes:
                    self._nodes[sub] = self._create_instance(sub, parent=self)
                return self._nodes[sub].set("#"+rest, value, create_nodes)
            self.set_value(rest, value)
        else:
            raise NotImplementedError("setting nodes is not implemented yet")

    def _pprint(self, level=0, indentation="   "):
        o = indentation*level + self.name

        if len(self._values) == 0 and len(self._nodes) == 0:
            if len(self.name) > 0:
                o += " "
            o += "{}\n"
            return o

        if len(self.name) > 0:
            o += " "
        o += "{"
        if len(self._values) > 0 or len(self._nodes) > 0:
            o += "\n"
        for n,v in self._values.items():
            if v is None:
                o += indentation*(level+1) + n + ";\n"
            else:
                o += indentation*(level+1) + n + " " + v + ";\n"
        for n in self._nodes.values():
            o += n._pprint(level+1, indentation)
        o += indentation*level + "}\n"
        return o

    def pprint(self, indentation="\t"):
        print( self._pprint(0, indentation) )

    def _print_data_header(self, level=0, indentation="    "):
        out = ""
        out += indentation*level +  type(self).__name__ + "(\n"
        level += 1

        out += self._print_data(level, indentation)

        level -= 1
        out += indentation*level + ")\n"

        return out

    def _print_data(self, level=0, indentation="    "):
        out = ""

        out += indentation*level + "'values': {\n"
        level += 1
        for k,v in self._values.items():
            out += indentation*level + '%s: %s,\n' % (repr(k), repr(v))
        level -= 1
        out += indentation*level + "},\n"

        out += indentation*level + "'nodes': {\n"
        level += 1
        for k,v in self._nodes.items():
            out += indentation*level + '"%s": ' % k
            out += type(self._nodes[k]).__name__ + "(\n"
            level += 1

            out += self._nodes[k]._print_data(level, indentation)

            level -= 1
            out += indentation*level + ")\n"
        level -= 1
        out += indentation*level + "},\n"

        return out

    def print_data(self, indentation="    "):
        print( self._print_data_header(0, indentation) )

    #-- methods for indexing etc

    def iter_nodes(self):
        for n in self._nodes:
            yield n

    #-- special methods for indexing etc

    def __contains__(self, key):
        return key in self._nodes

    def __len__(self):
        return len(self._nodes)

    def __iter__(self):
        return self._nodes.__iter__()

    def get_nodes(self):
        return list(self.iter_nodes())

    def __getitem__(self, key):
        """
            @rtype: NameValueNode
        """
        return self.get(key)

    def __setitem__(self, key, value):
        if isinstance(key, tuple) or isinstance(key, list):
            path, create_nodes = key
        else:
            path, create_nodes = key, False
        self.set(path, value, create_nodes)


class ExtendedNameValueNode(NameValueNode):
    """
        Like NameValueNode but nodes can inherit from others

        base {
            a;
        }
        node : base {
            b;
        }

        becomes:

        ExtendedNameValueNode(
            values {}
            nodes {
                "base": ExtendedNameValueNode(
                    "values": {
                        "a": None
                    }
                )

                "node": ExtendedNameValueNode(
                    "values": {
                        "a": None //-- inherited from base
                        "b": None
                    }
                )
            }
        )
    """

    def __init__(self, name="", parent=None):
        NameValueNode.__init__(self, name, parent)
        self.base = ""
        self.base_node = None
        self.is_abstract = False

    def clone(self):
        clone = self._create_instance(self.name, self.parent)
        clone.base = self.base
        clone.base_node = self.base_node
        clone._values = dict(self._values)
        for k,v in self._nodes.items():
            clone._nodes[k] = v.clone()
        return clone

    def get_dict(self):
        return self.name, {
            "base": self.base,
            "values": self._values,
            "nodes": dict([ i.get_dict() for i in self._nodes.values() ])
        }

    def get_base_node(self):
        if len(self.base) == 0:
            return None

        root = self.get_root()
        if root is None:
            raise ParseError("could not get root node for '%s'" % self.name)

        node = root.get(self.base)
        if node is None:
            raise ParseError("could not find node '%s'" % self.base)

        return node

    def set_base(self, base):
        self.base = base
        try:
            self.base_node = self.get_base_node()
            self.inherit(self.base_node)
        except KeyError:
            self.get_root().pprint()
            raise ParseError("could not find base node '%s' for node '%s'" % (self.base, self.name))

    #-- indexing etc

    def is_derived_from(self, base):
        if self.base == base:
            return True
        if not self.base_node is None:
            return self.base_node.is_derived_from(base)
        return False

    def get_derived_nodes(self, base, include_abstract=False):
        for node in self:
            if not node.is_derived_from(base):
                continue
            if node.is_abstract and not include_abstract:
                continue
            yield node

    #-- special methods

    def __len__(self):
        return len(list(self.iter_inherited()))

    def __iter__(self):
        return self._nodes.values().__iter__()

    #-- parsing

    def _on_open_node(self, name, body):
        if len(name) == 0:
            raise ParseError("empty node name")

        if name.startswith("@"):
            is_abstract = True
            name = name[1:]
        else:
            is_abstract = False

        if ":" in name:
            name, base = [ i.strip() for i in name.split(":",1) ]
        else:
            base = ""

        node = self._create_instance(name)
        node.is_abstract = is_abstract
        node.parent = self
        node.set_base(base)

        node._parse(body)

        if name in self._nodes:
            self._nodes[name].inherit(node)
        else:
            self._nodes[name] = node

        return True

    def _pprint(self, level=0, indentation="   "):
        o = indentation*level + self.name

        if len(self._values) == 0 and len(self._nodes) == 0:
            if len(self.base) > 0:
                o += " : " + self.base
            if len(self.name) > 0:
                o += " "
            o += "{}\n"
            return o

        if len(self.base) > 0:
            o += " : " + self.base
        if len(self.name) > 0:
            o += " "
        o += "{"
        if len(self._values) > 0 or len(self._nodes) > 0:
            o += "\n"
        for n,v in self._values.items():
            if v is None:
                o += indentation*(level+1) + n + ";\n"
            else:
                o += indentation*(level+1) + n + " " + v + ";\n"

        for n in self._nodes.values():
            if len(n.base) > 0:
                continue
            o += n._pprint(level+1, indentation)
        for n in self._nodes.values():
            if len(n.base) == 0:
                continue
            o += n._pprint(level+1, indentation)

        o += indentation*level + "}\n"
        return o

class ExtendedConfig(ExtendedNameValueNode):
    def __init__(self):
        ExtendedNameValueNode.__init__(self, name="", parent=None)
        self._node_type = ExtendedNameValueNode

    def load(self, path):
        self.file = path
        with open(path, "r") as fp:
            self.read(fp)