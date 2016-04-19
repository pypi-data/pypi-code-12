# -*- coding: utf-8 -*-
# :Project:   PatchDB -- Script execution contexts
# :Created:   Wed Nov  5 17:32:16 2003
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2003, 2014, 2016 Lele Gaifax
#

from __future__ import absolute_import, unicode_literals

import logging

logger = logging.getLogger('context')


class ExecutionError(Exception):
    """
    Exception raised on execution errors.
    """


class ExecutionContext(object):
    """
    An instance of this class is able to execute a script in some
    particular language. This is somewhat abstract and must be
    subclassed and attached to a database...

    Another responsibility of this class instances is to keep
    a persistent knowledge about last applied revision of
    a given script.
    """

    language_name = None

    execution_contexts_registry = {}
    user_assertions = {}

    @classmethod
    def for_language(cls, language):
        """
        Return the right execution context for the given `language`.
        """

        return cls.execution_contexts_registry.get(language)

    @classmethod
    def execute(cls, patch, options):
        """
        Execute the given `patch` in the right context.
        """

        ctx = cls.execution_contexts_registry.get(patch.language)
        if ctx:
            if options.assume_already_applied:
                logger.warning("Considering %s %s as applied", patch.language, patch)
                cls.execution_contexts_registry['sql'].applied(patch)
            else:
                logger.info("Executing %s %s", patch.language, patch)
                ctx.apply(patch, options)
        else:
            raise ExecutionError("Not able to execute %s %s" %
                                 (patch.language, patch))

    def __init__(self):
        """
        Insert this context instance in the registry.
        """

        if self.language_name:
            registry = self.execution_contexts_registry
            assert self.language_name not in registry
            registry[self.language_name] = self
        self.assertions = {}

    def __getitem__(self, patchid):
        """
        Always return None, used by doctests.
        """

    def __setitem__(self, patchid, revision):
        """
        Do nothing, used by doctests.
        """

    def addAssertions(self, assertions):
        """
        Add given `assertions` to the set of assertions managed by the context.
        """

        for assertion in assertions:
            if "=" in assertion:
                assertion, state = assertion.split('=')
                state = state.lower() in ('true', 't', '1', 'yes', 'y')
            else:
                state = True
            if assertion in self.assertions:
                raise ValueError('Cannot override existing "%s" assertion' %
                                 assertion)
            self.user_assertions[assertion] = state

    def verifyCondition(self, condition):
        """
        Verify given `condition`, returning False if it is not satisfied.
        """

        return (self.assertions.get(condition, False)
                or self.user_assertions.get(condition, False))

    def apply(self, patch, options):
        "Try to execute the given `patch` script"

        raise NotImplementedError('Subclass responsibility')


def get_context_from_args(args):
    "Create and return the right execution context for the given CLI arguments"

    if args.postgresql:
        from .postgres import PostgresContext
        return PostgresContext(dsn=args.postgresql)

    if args.firebird:
        from .firebird import FirebirdContext
        return FirebirdContext(dsn=args.firebird,
                               username=args.username, password=args.password)

    if args.mysql:
        from .mysql import MySQLContext
        return MySQLContext(host=args.host, port=args.port, db=args.mysql,
                            username=args.username, password=args.password,
                            charset=args.charset, driver=args.driver)

    if args.sqlite:
        from .sqlite import SQLiteContext
        return SQLiteContext(database=args.sqlite)

    # The SA driver may be not present
    sauri = getattr(args, 'sqlalchemy', None)
    if sauri is not None:
        from .alchemy import SQLAlchemyContext
        return SQLAlchemyContext(url=sauri)


# Register the context for Python, always available
from .python import PythonContext
PythonContext()
