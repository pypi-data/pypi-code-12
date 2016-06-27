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

from link.dbrequest.driver import Driver

from copy import deepcopy


@Configurable(
    paths='{0}/manager.conf'.format(CONF_BASE_PATH),
    conf=category('QUERY')
)
class QueryManager(Middleware):
    """
    Manage storage backend and provide query system for it.

    :param backend: Storage backend
    :type backend: Driver
    """

    __constraints__ = [Driver]
    __protocols__ = ['query']

    def from_ast(self, ast):
        """
        Create a query from the provided AST.

        :param ast: AST
        :type ast: list

        :rtype: Query

        :raises ASTError: if provided AST is not valid.
        """

        self.validate_ast(ast)

        q = Query(self)
        q.ast = deepcopy(ast)

        return q

    def all(self):
        """
        Get a query selecting all elements in store.

        :rtype: Query
        """

        return Query(self)

    def get(self, condition):
        """
        Get a single element matching the filter.

        :param condition: Filter
        :type condition: C or CombinedCondition

        :returns: Matching element or None
        :rtype: Model or None
        """

        if not isinstance(condition, (C, CombinedCondition)):
            raise TypeError('Supplied condition is not supported: {0}'.format(
                type(condition)
            ))

        return self.execute(AST('get', condition.get_ast()))

    def create(self, *fields):
        """
        Put a new element into the store.

        :param fields: List of assignments
        :type fields: list of A

        :returns: Created element
        :rtype: Model
        """

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
        """
        Validate AST semantics.

        :raises ASTError: if the AST semantics are not valid
        """

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
                'count',
                'slice',
                'group'
            ]
            last_statements = ['update', 'delete', 'get', 'count', 'group']
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
        """
        Send query to the storage driver.

        :param ast: AST describing the query
        :type ast: dict or list

        :returns: storage driver's response
        """

        self.validate_ast(ast)

        if isinstance(ast, dict):
            if ast['name'] == 'get':
                elements = self.get_child_middleware().find_elements(
                    ast['val']
                )

                if len(elements) == 0:
                    return None

                else:
                    return elements[0]

            elif ast['name'] == 'create':
                return self.get_child_middleware().put_element(ast['val'])

        elif len(ast) == 0:
            return self.get_child_middleware().find_elements(ast)

        elif ast[-1]['name'] == 'update':
            return self.get_child_middleware().update_elements(
                ast[:-1],
                ast[-1]['val']
            )

        elif ast[-1]['name'] == 'delete':
            return self.get_child_middleware().remove_elements(ast[:-1])

        elif ast[-1]['name'] == 'count':
            return self.get_child_middleware().count_elements(ast[:-1])

        else:
            result = self.get_child_middleware().find_elements(ast)

            if ast[-1]['name'] == 'get':
                if len(result) == 0:
                    result = None

                else:
                    result = result[0]

            return result


class Query(object):
    """
    Database agnostic query.

    :param manager: Manager that will execute this query
    :type manager: QueryManager
    """

    def __init__(self, manager, *args, **kwargs):
        super(Query, self).__init__(*args, **kwargs)

        self.manager = manager
        self.ast = []
        self.result = None

    def _copy(self):
        """
        Create a copy of this query.

        :returns: Copy
        :rtype: Query
        """

        c = Query(self.manager)
        c.ast = deepcopy(self.ast)
        return c

    def to_ast(self):
        """
        Returns a copy of query's AST

        :returns: AST
        :rtype: list
        """

        return deepcopy(self.ast)

    def count(self):
        """
        Count elements matched by this query.

        :returns: Number of matching elements
        :rtype: int
        """

        c = self._copy()
        c.ast.append(AST('count', None))

        return self.manager.execute(c.ast)

    def get(self, condition):
        """
        Add filter to the query, and get a single element matching the query.

        :param condition: Filter
        :type condition: C or CombinedCondition

        :returns: Matching element or None
        :rtype: Model or None
        """

        c = self._copy()

        if not isinstance(condition, (C, CombinedCondition)):
            raise TypeError('Supplied condition is not supported: {0}'.format(
                type(condition)
            ))

        c.ast.append(AST('get', condition.get_ast()))

        return self.manager.execute(c.ast)

    def filter(self, condition):
        """
        Returns a new query with a new filter added.

        :param condition: Filter
        :type condition: C or CombinedCondition

        :returns: Query
        :rtype: Query
        """

        c = self._copy()

        if not isinstance(condition, (C, CombinedCondition)):
            raise TypeError('Supplied condition is not supported: {0}'.format(
                type(condition)
            ))

        c.ast.append(AST('filter', condition.get_ast()))

        return c

    def exclude(self, condition):
        """
        Returns a new query with a new (negated) filter added.

        :param condition: Filter
        :type condition: C or CombinedCondition

        :returns: Query
        :rtype: Query
        """

        c = self._copy()

        if not isinstance(condition, (C, CombinedCondition)):
            raise TypeError('Supplied condition is not supported: {0}'.format(
                type(condition)
            ))

        c.ast.append(AST('exclude', condition.get_ast()))

        return c

    def __getitem__(self, s):
        """
        Returns a new query with a slice of filtered elements.

        :param s: query's slice
        :type s: slice

        :returns: Query
        :rtype: Query
        """

        c = self._copy()

        if not isinstance(s, slice):
            s = slice(s)

        c.ast.append(AST('slice', s))

        return c

    def __iter__(self):
        """
        Executes the query and iterate through the result.

        :returns: iterator on query's result
        :rtype: iterator
        """

        if self.result is None:
            self.result = self.manager.execute(self.ast)

        return iter(self.result)

    def update(self, *fields):
        """
        Update elements matching the query.

        :param fields: Assignments
        :type fields: list of A

        :returns: Number of modified elements.
        :rtype: int
        """

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
        """
        Delete elements matching the query.

        :returns: Number of deleted elements.
        :rtype: int
        """

        c = self._copy()
        c.ast.append(AST('delete', None))

        return self.manager.execute(c.ast)

    def group(self, key, *expressions):
        """
        Group elements by key matching the query using the expressions.

        :param key: Key used to group elements
        :type key: str

        :param expressions: Expressions
        :type expressions: list of CombinableExpression

        :returns: Grouped elements.
        """

        c = self._copy()
        c.ast.append(AST('group', {
            'key': key,
            'expressions': [
                expression.get_ast()
                for expression in expressions
            ]
        }))

        return self.manager.execute(c.ast)
