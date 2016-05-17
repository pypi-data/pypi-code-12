# -*- coding: utf-8 -*-
# :Project:   PatchDB -- Generic SQL script execution context
# :Created:   sab 31 mag 2014 13:00:48 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2014, 2016 Lele Gaifax
#

from __future__ import unicode_literals

from datetime import datetime
from hashlib import md5 as hash_factory
import re

from ..states import State
from . import logger
from . import ExecutionContext, ExecutionError


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

        from re import split, MULTILINE
        from sys import stderr

        cursor = self.connection.cursor()
        stmts = split(r'^\s*;;\s*$', patch.script, flags=MULTILINE)

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

        return stmt.startswith('drop ')

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


class FakeDataDomainsMixin(object):
    "Mixin implementing poor man's `data domains` for simplicistic databases."

    create_domain_rx = re.compile(r'^create\s+domain\s+(.*)$', re.IGNORECASE)
    name_definition_rx = re.compile(r'([a-zA-Z_]+'
                                    r'|"[a-zA-Z_]+"'
                                    r'|`[a-zA-Z_]+`)'
                                    r'\s+(.+)$')
    create_table_rx = re.compile(r'^create\s+table\s+', re.IGNORECASE)

    data_domains = {}

    def prepareStatement(self, statement):
        """Handle user defined data domains.

        Intercept ``CREATE DOMAIN`` statements and handle them directly,
        replace known domains in ``CREATE TABLE`` statements.
        """

        statement = statement.strip()
        cd = self.create_domain_rx.match(statement)
        if cd is not None:
            defn = cd.group(1)
            match = self.name_definition_rx.match(defn)
            if match is not None:
                name = match.group(1)
                definition = match.group(2)
                self.data_domains[name] = definition
                return None

        if self.data_domains and self.create_table_rx.match(statement):
            fdd_names = []
            for name in self.data_domains:
                if name[0] in '"`':
                    fdd_names.append(name)
                else:
                    fdd_names.append(''.join('_' if c=='_' else ('['+c+c.upper()+']')
                                             for c in name.lower()))
            fdd_rx = r"(?<![\w'])(%s)(?![\w'])" % '|'.join(fdd_names)
            statement = re.sub(fdd_rx,
                               lambda m, dd=self.data_domains:
                               dd[m.group(1) if m.group(1)[0] in '"`' else m.group(1).lower()],
                               statement)

        return statement
