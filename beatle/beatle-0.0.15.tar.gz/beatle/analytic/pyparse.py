# -*- coding: utf-8 -*-
"""The mission of this module is analyzing python code and
recreate hist structure"""

import ast
from analytic import astd
import model


class pyparse(object):
    """Class for parsing a python text"""

    project = None

    @classmethod
    def set_project(this, project):
        """Sets the project"""
        pyparse.project = project

    def __init__(self, container, text):
        """Initializes the parser and do the work"""
        super(pyparse, self).__init__()
        self._outlines = []  # the set of lines to remove
        self._container = container
        self._text = text
        self._set_handlers()
        self._status = self.analize()

    def __imports_folder(self, parent):
        """Access or create to import folder"""
        s = parent[model.py.ImportsFolder]
        if len(s):
            return s[0]
        kwargs = {'parent': parent}
        return model.py.ImportsFolder(**kwargs)

    def inline(self):
        """This method returns the text without what whas processed"""
        l = ['0'] + self._text.splitlines()
        u = [l[i] for i in range(1, len(l)) if i not in self._outlines]
        return '\n'.join(u)

    def _set_handlers(self):
        """The ast tree is composed by several types of nodes
        each one representing a kind of python expression.
        This method setup the handlers for each one type of
        nodes"""
        self._handler = {
            ast.Expr: self.process_expr,
            ast.Import: self.process_import,
            ast.ImportFrom: self.process_import_from,
            ast.ClassDef: self.process_class_def,
            ast.FunctionDef: self.process_function_def,
            ast.Assign: self.process_var
            }

        self._text_handler = {
            ast.Expr: self._text_expr,
            ast.Attribute: self._text_attribute,
            ast.Name: self._text_name,
            ast.Str: self._text_str,
            ast.Num: self._num_str,
            ast.BinOp: self._binop_str,
            ast.Add: self._add_str,
            ast.Sub: self._sub_str,
            ast.Mult: self._mult_str,
            ast.Div: self._div_str,
            ast.FloorDiv: self._floordiv_str,
            ast.Mod: self._mod_str,
            ast.Pow: self._pow_str,
            ast.LShift: self._lshift_str,
            ast.RShift: self._rshift_str,
            ast.BitOr: self._bitor_str,
            ast.BitXor: self._bitxor_str,
            ast.BitAnd: self._and_str,
            ast.keyword: self._keyword_str,
            ast.Dict: self._dict_str,
            ast.Tuple: self._tuple_str,
            ast.List: self._list_str,
            ast.Subscript: self._subscript_str,
            ast.Index: self._index_str,
            ast.Call: self._call_str,
            ast.UnaryOp: self._unary_str,
            }

    def call_handler(self, parent, node):
        """Do the call"""
        return self._handler.get(type(node), self.process_none)(parent, node)

    def process_node(self, parent, node):
        """This is the root of process analysing"""
        for child_node in ast.iter_child_nodes(node):
            self.call_handler(parent, child_node)
        return True

    def text_node(self, node):
        """This represents the text converter"""
        self.outline(node)
        return self._text_handler.get(type(node), self.text_none)(node)

    def text_none(self, node):
        """This represents the missing handler case"""
        print '\nmissing handler for {t}'.format(t=type(node))
        return ''

    def process_none(self, parent, node):
        """Do an empty process for unknown nodes"""
        return True

    def process_expr(self, parent, node):
        """Add comment to parent"""
        self.outline(node)
        parent.note = self.text_node(node.value).strip()[1:-1]

    def process_import(self, parent, node):
        """Process a import node"""
        if len(node.names):
            kwargs = {'parent': self.__imports_folder(parent)}
            for n in node.names:
                kwargs['name'] = n.name
                kwargs['as'] = n.asname
                model.py.Import(**kwargs)
        self.outline(node)
        return True

    def process_import_from(self, parent, node):
        """Process a import from node"""
        if len(node.names):
            kwargs = {
                'parent': self.__imports_folder(parent),
                'name': node.module
            }
            for n in node.names:
                kwargs['from'] = n.name
                kwargs['as'] = n.asname
                model.py.Import(**kwargs)
        self.outline(node)
        return True

    def process_class_def(self, parent, node):
        """Process a class definition"""
        kwargs = {
            'parent': parent,
            'name': node.name,
            'raw': True,
            'note': ast.get_docstring(node, False) or ''
            }
        if not kwargs['note']:
            i = 0
        else:
            i = 1
        # the base classes must be resolved later
        cls = model.py.Class(**kwargs)
        # annotate bases for later resolution
        if node.bases:
            if pyparse.project:
                kwargs['parent'] = cls
                kwargs['raw'] = True
                for base in node.bases:
                    kwargs['ancestor'] = None
                    kwargs['name'] = self.text_node(base)
                    model.py.Inheritance(**kwargs)
            else:
                cls._bases = node.bases
        for j in range(i, len(node.body)):
            self.call_handler(cls, node.body[j])
        self.outline(node)
        return True

    def process_var(self, parent, node):
        """Process a single global asign"""
        kwargs = {'parent': parent, 'value': self.text_node(node.value)}
        if type(parent) is model.py.Class:
            theClass = model.py.MemberData
        else:
            theClass = model.py.Data
        for v in node.targets:
            if type(v) is not ast.Name:
                # we dont implement this
                continue
            kwargs['name'] = v.id
            self.outline(v)
            theClass(**kwargs)
        return True

    def process_decorator(self, parent, node):
        """Process a decorator node"""
        kwargs = {'parent': parent}
        if type(node) is ast.Name:
            kwargs['name'] = '{node.id}'.format(node=node)
        if type(node) is ast.Call:
            kwargs['call'] = True
            kwargs['name'] = self.text_node(node.func)
        else:
            kwargs['name'] = self.text_node(node)
        deco = model.py.Decorator(**kwargs)
        if type(node) is ast.Call:
            for arg in node.args:
                self.process_arg_def(deco, arg, context='value')
        return True

    def _text_expr(self, node):
        """process a ast.Expr"""
        return self.text_node(node.value)

    def _text_attribute(self, node):
        """process a ast.Attribute"""
        attr = node.attr
        if node.value:
            value = self.text_node(node.value)
            return '{value}.{attr}'.format(value=value, attr=attr)
        return attr

    def _text_name(self, node):
        """process ast.Name"""
        return node.id

    def _text_str(self, node):
        """process a ast.Str"""
        if '"' in node.s:
            return "'{node.s}'".format(node=node)
        return '"{node.s}"'.format(node=node)

    def _num_str(self, node):
        """process a ast.Num"""
        return "{node.n}".format(node=node)

    def _binop_str(self, node):
        """process ast.BinOp"""
        left = self.text_node(node.left)
        right = self.text_node(node.right)
        operand = self.text_node(node.op)
        return '{left} {operand} {right}'.format(
            left=left, right=right, operand=operand)

    def _add_str(self, node):
        """process ast.Add"""
        return '+'

    def _sub_str(self, node):
        """process ast.Sub"""
        return '-'

    def _mult_str(self, node):
        """process ast.Mult"""
        return '*'

    def _div_str(self, node):
        """process ast.Div"""
        return '/'

    def _floordiv_str(self, node):
        """process ast.FloorDiv"""
        return '//'

    def _mod_str(self, node):
        """process ast.Mod"""
        return '%'

    def _pow_str(self, node):
        """process ast.Pow"""
        return '**'

    def _lshift_str(self, node):
        """process ast.LShift"""
        return '<<'

    def _rshift_str(self, node):
        """process ast.RShift"""
        return '>>'

    def _bitor_str(self, node):
        """process ast.BitOr"""
        return '|'

    def _bitxor_str(self, node):
        """process ast.BitXor"""
        return '^'

    def _and_str(self, node):
        """process ast.BitAnd"""
        return '&'

    def _keyword_str(self, node):
        """process ast.keyword"""
        value = self.text_node(node.value)
        arg = node.arg
        return '{arg}={value}'.format(arg=arg, value=value)

    def _dict_str(self, node):
        """process ast.Dict"""
        assert(len(node.keys) == len(node.values))
        return '{{{cnt}}}'.format(cnt=', '.join(['{k}: {v}'.format(
            k=self.text_node(node.keys[i]),
            v=self.text_node(node.values[i])) for i in range(0, len(node.keys))]))

    def _tuple_str(self, node):
        """process ast.Tuple"""
        return '({cnt})'.format(cnt=', '.join([self.text_node(k) for k in node.elts]))

    def _list_str(self, node):
        """process ast.List"""
        return '[{cnt}]'.format(cnt=', '.join([self.text_node(k) for k in node.elts]))

    def _subscript_str(self, node):
        """process ast.Subscript"""
        name = self.text_node(node.name)
        _slice = self.text_node(node.slice)
        return '{name}[{slice}]'.format(name=name, slice=_slice)

    def _index_str(self, node):
        """process ast.Index"""
        return self.text_node(node.value)

    def _call_str(self, node):
        """process ast.Call"""
        args = [self.text_node(x) for x in node.args or []]
        args.extend([self.text_node(x) for x in node.keywords])
        if node.starargs:
            args.append('*{}'.format(self.text_node(node.starargs)))
        if node.kwargs:
            args.append('**{}'.format(self.text_node(node.kwargs)))
        func = self.text_node(node.func)
        args = ', '.join(args)
        return '{func}({args})'.format(func=func, args=args)

    def _unary_str(self, node):
        """process ast.UnaryOp"""
        if type(node.op) == ast.Invert:
            return '~{}'.format(self.text_node(node.operand))
        elif type(node.op) == ast.Not:
            return 'not {}'.format(self.text_node(node.operand))
        elif type(node.op) == ast.UAdd:
            return '+{}'.format(self.text_node(node.operand))
        elif type(node.op) == ast.USub:
            return '-{}'.format(self.text_node(node.operand))
        else:
            return self.text_none(node)

    def process_arg_def(self, parent, node, **kwargs):
        """Process an argument node"""
        self.outline(node)
        kwargs = {
            'parent': parent,
            'name': self.text_node(node),
            'default': kwargs.get('default', ''),
            'context': kwargs.get('context', 'declare')
            }
        model.py.Argument(**kwargs)
        return True

    def process_function_def(self, parent, node):
        """Process a function definition"""
        kwargs = {
            'parent': parent,
            'name': node.name,
            'raw': True
            }
        for deco in node.decorator_list:
            self.outline(deco)
        if node.lineno not in self._outlines:
            self._outlines.append(node.lineno)
        # get the comment if any
        line = None
        if len(node.body) > 0:
            line = node.body[0].lineno
            col = node.body[0].col_offset
            if type(node.body[0]) is ast.Expr:
                if type(node.body[0].value) is ast.Str:
                    self.outline(node.body[0])
                    line = node.body[0].to_lineno + 1
                    kwargs['note'] = node.body[0].value.s
        #line = max(self._outlines) + 1
        if type(parent) is model.py.Class:
            """Se trata de una funcion miembro"""
            if node.name == '__init__':
                function = model.py.InitMethod(**kwargs)
            else:
                function = model.py.MemberMethod(**kwargs)
        else:
            function = model.py.Function(**kwargs)
        #Ok, add decorators
        for deco in node.decorator_list:
            self.process_decorator(function, deco)
        #Ok, add arguments
        kwargs['parent'] = function
        kwargs['note'] = ''
        v = node.args.defaults
        i = len(v)
        k = len(node.args.args)
        for arg in node.args.args:
            # this is valid for python3. For the moment, we
            # work in python 2
            #self.call_handler(function, arg)
            if k > i:
                self.process_arg_def(function, arg)
            else:
                self.process_arg_def(function, arg, default=self.text_node(v[-i]))
                i = i - 1
            k = k - 1
        if node.args.vararg is not None:
            model.py.ArgsArgument(**kwargs)
        if node.args.kwarg is not None:
            model.py.KwArgsArgument(**kwargs)
        #push all lines
        self.outline(node)
        #now, extract content from lines
        if line:
            code = [0] + self._text.splitlines()
            code = [code[i] for i in range(line, node.to_lineno + 1)]
            lcode = len(code)
            if lcode:
                try:
                    i = (n for n in range(0, lcode) if len(code[n].strip()) > 0).next()
                    test = code[i]
                    extra = len(test) - len(test.lstrip())
                    fcode = []
                    if extra:
                        # filter comments that will be addeded and cutted wrong
                        for i in range(0, lcode):
                            s = code[i]
                            if len(s.strip()) and len(s[:extra].strip()):
                                continue
                            else:
                                fcode.append(s)
                        lcode = len(fcode)
                        code = fcode
                        code = [code[i][extra:] for i in range(0, lcode)]
                        col -= extra
                        if col < 0:
                            col = 0
                except:
                    pass
            #en la primera linea del codigo hemos de tratar de todas maneras la columna
            #por si se trata de una expresion inline
            if code:
                try:
                    code[0] = code[0][col:]
                    function._content = '\n'.join(code)
                except:
                    print "col bug"
                #for some reason, some nodes are not simply traveled as childs
        return True

    def outline(self, node):
        """This method adds the lines represented by the node
        and his childs to the _outlines"""
        if hasattr(node, 'lineno'):
            s = node.lineno
            if hasattr(node, 'to_lineno'):
                t = node.to_lineno
                if s and t:
                    for i in range(s, t + 1):
                        if i not in self._outlines:
                            self._outlines.append(i)
                    return
            if s is not None and s not in self._outlines:
                self._outlines.append(s)
        for child_node in ast.iter_child_nodes(node):
            self.outline(child_node)

    def analize(self):
        """This method analizes the code"""
        import traceback
        import sys
        try:
            tree = astd.parse(self._text)
            return self.process_node(self._container, tree)
        except Exception as inst:
            traceback.print_exc(file=sys.stdout)
            print type(inst)     # the exception instance
            print inst.args      # arguments stored in .args
            print inst
            return False



