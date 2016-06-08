# -*- coding: utf-8 -*-

from b3j0f.conf import Configurable, category

from link.middleware.core import Middleware
from link.dbrequest import CONF_BASE_PATH

from link.dbrequest.ast import AST
from link.dbrequest.ast import ASTSingleStatementError
from link.dbrequest.ast import ASTLastStatementError
from link.dbrequest.ast import ASTInvalidStatementError
from link.dbrequest.ast import ASTInvalidFormatError

from link.dbrequest.comparison import C, CombinedCondition
from link.dbrequest.assignment import A


@Configurable(
    paths='{0}/manager.conf'.format(CONF_BASE_PATH),
    conf=category('QUERY')
)
class QueryManager(Middleware):

    __protocols__ = ['query']

    def __init__(self, backend, *args, **kwargs):
        super(QueryManager, self).__init__(*args, **kwargs)

        if not isinstance(backend, Middleware):
            raise TypeError('Provided backend is not a middleware')

        self.backend = backend

    def all(self):
        return Query(self)

    def get(self, condition):
        if not isinstance(condition, (C, CombinedCondition)):
            raise TypeError('Supplied condition is not supported: {0}'.format(
                type(condition)
            ))

        return self.execute(AST('get', condition.get_ast()))

    def create(self, *fields):
        fields_ast = []

        for field in fields:
            if not isinstance(field, A):
                raise TypeError('Supplied field is not supported: {0}'.format(
                    type(field)
                ))

            fields_ast.append(field.get_ast())

        return self.execute(AST('create', fields_ast))

    @staticmethod
    def validate_ast(ast):
        if isinstance(ast, dict):
            if ast['name'] not in ['get', 'create']:
                raise ASTSingleStatementError(ast['name'])

        elif isinstance(ast, list):
            statements = [
                'get',
                'filter',
                'exclude',
                'update',
                'delete',
                'count'
            ]
            last_statements = ['update', 'delete', 'get', 'count']
            l = len(ast)

            for i in range(l):
                node = ast[i]

                if node['name'] in last_statements and (i + 1) != l:
                    raise ASTLastStatementError(node['name'], i)

                elif node['name'] not in statements:
                    raise ASTInvalidStatementError(node['name'])

        else:
            raise ASTInvalidFormatError()

    def execute(self, ast):
        self.validate_ast(ast)

        if isinstance(ast, dict):
            if ast['name'] == 'get':
                elements = self.backend.find_elements(ast['val'])

                if len(elements) == 0:
                    return None

                else:
                    return elements[0]

            elif ast['name'] == 'create':
                return self.backend.put_element(ast['val'])

        elif ast[-1]['name'] == 'update':
            return self.backend.update_elements(
                ast[:-1],
                ast[-1]['val']
            )

        elif ast[-1]['name'] == 'delete':
            return self.backend.remove_elements(ast[:-1])

        elif ast[-1]['name'] == 'count':
            return self.backend.count_elements(ast[:-1])

        else:
            return self.backend.find_elements(ast)


class Query(object):
    def __init__(self, manager, *args, **kwargs):
        super(Query, self).__init__(*args, **kwargs)

        self.manager = manager
        self.ast = []
        self.result = None

    def _copy(self):
        c = Query(self.manager)
        c.ast = self.ast
        return c

    def count(self):
        c = self._copy()
        c.ast.append(AST('count', None))

        return self.manager.execute(c.ast)

    def get(self, condition):
        c = self._copy()

        if not isinstance(condition, (C, CombinedCondition)):
            raise TypeError('Supplied condition is not supported: {0}'.format(
                type(condition)
            ))

        c.ast.append(AST('get', condition.get_ast()))

        return self.manager.execute(c.ast)

    def filter(self, condition):
        c = self._copy()

        if not isinstance(condition, (C, CombinedCondition)):
            raise TypeError('Supplied condition is not supported: {0}'.format(
                type(condition)
            ))

        c.ast.append(AST('filter', condition.get_ast()))

        return c

    def exclude(self, condition):
        c = self._copy()

        if not isinstance(condition, (C, CombinedCondition)):
            raise TypeError('Supplied condition is not supported: {0}'.format(
                type(condition)
            ))

        c.ast.append(AST('exclude', condition.get_ast()))

        return c

    def __getitem__(self, s):
        c = self._copy()

        if not isinstance(s, slice):
            s = slice(s)

        c.ast.append(AST('slice', s))

        return c

    def __iter__(self):
        if self.result is None:
            self.result = self.manager.execute(self.ast)

        return iter(self.result)

    def update(self, *fields):
        c = self._copy()

        fields_ast = []

        for field in fields:
            if not isinstance(field, A):
                raise TypeError('Supplied field is not supported: {0}'.format(
                    type(field)
                ))

            fields_ast.append(field.get_ast())

        c.ast.append(AST('update', fields_ast))

        return self.manager.execute(c.ast)

    def delete(self):
        c = self._copy()
        c.ast.append(AST('delete', None))

        return self.manager.execute(c.ast)
