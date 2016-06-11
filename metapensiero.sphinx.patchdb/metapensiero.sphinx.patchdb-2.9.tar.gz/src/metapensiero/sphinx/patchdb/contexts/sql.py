# -*- coding: utf-8 -*-
# :Project:   PatchDB -- Generic SQL script execution context
# :Created:   sab 31 mag 2014 13:00:48 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2014, 2016 Lele Gaifax
#

from __future__ import unicode_literals

from collections import deque
from datetime import datetime
from hashlib import md5 as hash_factory
try:
    from io import StringIO
except ImportError:
    from cStringIO import StringIO

from sqlparse.tokens import Comment, Keyword, Literal, Name, Punctuation, Whitespace
from sqlparse.lexer import Lexer

from ..states import State
from . import logger
from . import ExecutionContext, ExecutionError


def split_script(script):
    """Split the `script` into the single SQL statements.

    The script may be composed zero or more SQL statements, separated by two consecutive
    semicomma ``;;`` on a line by their own::

      CREATE DOMAIN integer_t INTEGER
      ;;
      CREATE DOMAIN string_t VARCHAR(20)

    Empty statements are discarded.
    """

    statements = []

    lines = []
    for line in script.splitlines():
        if line.strip() == ';;':
            statement = '\n'.join(lines)
            if statement.strip():
                statements.append(statement + '\n')
            lines = []
        else:
            lines.append(line)
    statement = '\n'.join(lines)
    if statement.strip():
        statements.append(statement + '\n')

    return statements


def valuable_tokens(statement):
    "Iterate over `statement`'s tokens, ignoring whitespace and comments."

    lexer = Lexer()
    for pos, type, value in lexer.get_tokens_unprocessed(StringIO(statement)):
        if not (type in Whitespace or type in Comment):
            yield pos, type, value


def statement_starts_with(statement, expected_tokens):
    """Determine whether `statement` starts with the given set of `expected_tokens`.

    Return ``None`` if not, otherwise the remaining tokens.
    """

    tokens = valuable_tokens(statement)

    for etoken in expected_tokens:
        this = next(tokens, None)
        if this is None:
            return None
        ttype = this[1]
        tvalue = this[2].upper()

        if isinstance(etoken, tuple):
            etoken = [etoken]

        for etype, evalue in etoken:
            if ttype == etype and tvalue == evalue:
                break
        else:
            tokens = None
            break

    return tokens


class SqlContext(ExecutionContext):
    """
    Generic SQL execution context.

    This is still somewhat abstract, subclasses must reimplement
    at least :method:`makeConnection()` and :method:`setupContext()`.
    """

    language_name = 'sql'

    GET_PATCH_REVISION_STMT = ("SELECT revision"
                               " FROM patchdb"
                               " WHERE patchid = %s")
    "The SQL statement used to get the applied revision of a given patch"

    INSERT_PATCH_STMT = ("INSERT INTO patchdb (patchid, revision, applied)"
                         " VALUES (%s, %s, %s)")
    "The SQL statement used to register the execution a new patch"

    UPDATE_PATCH_STMT = ("UPDATE patchdb"
                         " SET revision = %s, applied = %s"
                         " WHERE patchid = %s")
    "The SQL statement used to update the information of a given patch"

    GET_LAST_APPLIED_STMT = ("SELECT patchid, revision"
                             " FROM patchdb"
                             " ORDER BY applied DESC"
                             " LIMIT 1")
    "The SQL statement used to fetch the latest applied patch info"

    def __init__(self, **args):
        """Initialize the instance.

        Open the DB connection and execute the setup, if needed.
        """

        ExecutionContext.__init__(self)

        self.makeConnection(**args)
        self.setupContext()

        self._patches = None

    def __getitem__(self, patchid):
        """
        Get the applied revision of a given `patchid`, or None.
        """

        return self.patches.get(patchid)

    def __setitem__(self, patchid, revision):
        """
        Cache the given `revision` as the last applied version of `patchid`.
        """

        self.patches[patchid] = revision

    @property
    def patches(self):
        """
        Extract the applied patches info from the database, returning a
        dictionary mapping a patch id to its revision.
        """

        if self._patches is None:
            cursor = self.connection.cursor()
            cursor.execute("SELECT patchid, revision"
                           " FROM patchdb")
            patches = cursor.fetchall()
            cursor.close()

            self._patches = dict((patchid, revision) for patchid, revision in patches)

        return self._patches

    @property
    def state(self):
        "A tuple representing the latest applied patch."

        cursor = self.connection.cursor()
        cursor.execute("SELECT patchid, revision"
                       " FROM patchdb"
                       " ORDER BY patchid")

        hash = hash_factory()
        update = hash.update
        patchid = None
        for patchid, revision in cursor:
            signature = '%s@%s' % (patchid, revision)
            update(signature.encode('utf-8'))
        cursor.close()

        if patchid is not None:
            cursor = self.connection.cursor()
            cursor.execute(self.GET_LAST_APPLIED_STMT)
            last = cursor.fetchone()
            cursor.close()

            return State(hash.hexdigest(), last[0], last[1])

    def apply(self, patch, options):
        """
        Try to execute the given `patch` script, which may be
        composed by one or more SQL statements separated by two
        consecutive semicomma ``;;`` on a line by their own::

          CREATE DOMAIN integer_t INTEGER
          ;;
          CREATE DOMAIN string_t VARCHAR(20)

        If everything goes well, update the persistent status of
        the given `patch`, storing its `revision` in the ``patchdb``
        table in the database.
        """

        from sys import stderr

        cursor = self.connection.cursor()
        stmts = split_script(patch.script)

        last_good_point = None
        current_line = 1
        for i, stmt in enumerate(stmts):
            if stmt:
                stmt_lines = stmt.count('\n')
                stmt = self.prepareStatement(self.replaceUserVariables(stmt))
                if not stmt:
                    continue

                logger.debug("Executing '%s ...'" % stmt[:50])

                try:
                    cursor.execute(stmt)
                    current_line += stmt_lines + 1
                    last_good_point = i+1
                    self.savePoint(last_good_point)
                    if not options.verbose:
                        stderr.write('.')
                        stderr.flush()
                except Exception as e:
                    errmsg, syntaxerror, nonexistingobj = self.classifyError(e)

                    if (nonexistingobj
                        and patch.onerror != 'ignore'
                        and self.shouldIgnoreNonExistingObjectError(stmt.lstrip().lower())):
                        onerror = 'ignore'
                    else:
                        onerror = patch.onerror

                    if last_good_point:
                        self.rollbackPoint(last_good_point)
                    else:
                        self.connection.rollback()

                    if len(stmts)>1:
                        details = "statement at line %d of " % current_line
                    else:
                        details = ""

                    if onerror == 'abort' or syntaxerror:
                        logger.critical("Execution of %s%s generated an"
                                        " error: %s", details, patch, errmsg)
                        logger.debug("Statement: %s", stmt)
                        raise ExecutionError("Execution of %s%s generated an"
                                             " error: %s" %
                                             (details, patch, errmsg))
                    elif onerror == 'ignore':
                        logger.info("Ignoring error generated by %s%s: %s",
                                    details, patch, errmsg)
                        if not options.verbose:
                            stderr.write('I')
                            stderr.flush()
                    elif onerror == 'skip':
                        logger.info("Skipping succeding statements due to"
                                    " error executing %s%s: %s",
                                    details, patch, errmsg)
                        if not options.verbose:
                            stderr.write('S')
                            stderr.flush()
                        break

        self.applied(patch)

    def prepareStatement(self, statement):
        """Possibly adjust the given `statement` before execution.

        This implementation simply returns `statement.strip()`.
        Subclasses may apply arbitrary transformations to it, or return
        ``None`` to discard its execution.
        """

        return statement.strip()

    def classifyError(self, exc):
        """Determine the kind of error given its exception.

        Return a tuple (message, syntaxerror, nonexistingobj).
        """

        raise NotImplementedError('Subclass responsibility')

    def shouldIgnoreNonExistingObjectError(self, stmt):
        """Determine whether the “non existing object” error should be ignored."""

        return statement_starts_with(stmt, ((Keyword.DDL, 'DROP'),))

    def _recordAppliedInfo(self, pid, rev, _utcnow=datetime.utcnow):
        """Persist the knowledge on the database."""

        cursor = self.connection.cursor()

        cursor.execute(self.GET_PATCH_REVISION_STMT, (pid,))
        rec = cursor.fetchone()
        if rec is None:
            logger.debug('Inserting "%s@%s" into the database', pid, rev)
            cursor.execute(self.INSERT_PATCH_STMT, (pid, rev, _utcnow()))
        else:
            logger.debug('Updating "%s@%s" in the database', pid, rev)
            cursor.execute(self.UPDATE_PATCH_STMT, (rev, _utcnow(), pid))

        self[pid] = rev

    def applied(self, patch):
        """Register the given `patch` as *applied*.

        Update the persistent knowledge about the given `patch`,
        storing it's revision on the database. The same is done
        on all the patches this script may have upgraded.
        """

        if patch.brings:
            for pid,rev in patch.brings:
                self._recordAppliedInfo(pid, rev)
        self._recordAppliedInfo(patch.patchid, patch.revision)
        self.connection.commit()

    def makeConnection(self, **args):
        """Open the connection with the database."""

        raise NotImplementedError('Subclass responsibility')

    def closeConnection(self):
        self.connection.close()

    def setupContext(self):
        """Possibly create the tables used for persistent knowledge."""

        raise NotImplementedError('Subclass responsibility')

    def savePoint(self, point):
        """Possibly commit the work up to this point."""

    def rollbackPoint(self, point):
        """Possibly rollback to point."""

    def backup(self, backups_dir):
        logger.warning("%s does not implement the backup method!", type(self).__name__)

    def restore(self, backup):
        raise NotImplementedError("%s does not implement the restore method!"
                                  % type(self).__name__)


def is_create_domain(statement):
    "Determine whether the given `statement` is a ``CREATE DOMAIN``."

    return statement_starts_with(statement,
                                 ((Keyword.DDL, 'CREATE'),
                                  (Keyword, 'DOMAIN')))


def is_create_or_alter_table(statement):
    "Determine whether the given `statement` is a ``CREATE TABLE`` or an ``ALTER TABLE``."

    return statement_starts_with(statement,
                                 ([(Keyword.DDL, 'CREATE'), (Keyword.DDL, 'ALTER')],
                                  (Keyword, 'TABLE')))


def replace_fake_domains(statement, tokens, domains):
    maybe_schema_name = next(tokens, None)
    if maybe_schema_name is None:
        return statement

    maybe_dot = next(tokens, None)
    if maybe_dot is None:
        return statement

    if maybe_dot[1] == Punctuation and maybe_dot[2] == '.':
        table_name = next(tokens, None)
        if table_name is None:
            return statement

    fake_domains = []
    last2 = deque(maxlen=2)
    for token in tokens:
        if not (token[1] in Name or token[1] in Literal.String.Symbol):
            if len(last2) == 2 and last2[0][1] in Name and (
                    last2[1][1] in Name or last2[1][1] in Literal.String.Symbol):
                fake_domains.append(last2[1])
        last2.append(token)

    statement = list(statement)
    for pos, _, name in reversed(fake_domains):
        if name[0] not in '`"':
            name = name.lower()
        if name in domains:
            statement[pos:pos+len(name)] = list(domains[name])

    return ''.join(statement)


class FakeDataDomainsMixin(object):
    "Mixin implementing poor man's `data domains` for simplicistic databases."

    data_domains = {}

    def prepareStatement(self, statement):
        """Handle user defined data domains.

        Intercept ``CREATE DOMAIN`` statements and handle them directly,
        replace known domains in ``CREATE TABLE`` statements.
        """

        iscd = is_create_domain(statement)
        if iscd:
            name = next(iscd)[2]
            definition = statement[next(iscd)[0]:]
            if name[0] not in '`"':
                name = name.lower()
            self.data_domains[name] = definition
            return None

        if self.data_domains:
            isct = is_create_or_alter_table(statement)
            if isct:
                statement = replace_fake_domains(statement, isct, self.data_domains)

        return statement
