# -*- coding: utf-8 -*-
# :Project:   PatchDB -- Apply collected patches to a database
# :Created:   Wed Nov 12 23:10:22 2003
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2003, 2009, 2010, 2012, 2013, 2014, 2015, 2016 Lele Gaifax
#

from __future__ import absolute_import, print_function, unicode_literals

from os.path import isabs
import tempfile

import pkg_resources

from .contexts import ExecutionContext, ExecutionError, get_context_from_args
from .patch import DependencyError
from .manager import DuplicatedScriptError, patch_manager


OK, SOFTWARE, DATAERR, CONFIG, USAGE = 0, 1, 2, 3, 128


def path_spec(ps):
    if isabs(ps) or not ':' in ps:
        return ps
    pkgname, subpath = ps.split(':', 1)
    return pkg_resources.resource_filename(pkgname, subpath)


def main():
    import locale, logging
    from argparse import ArgumentParser

    locale.setlocale(locale.LC_ALL, '')

    parser = ArgumentParser(description="Database script applier")

    parser.add_argument("storage", type=path_spec, nargs='+',
                        help="One or more archives containing collected scripts."
                        " May be either plain file names or package relative paths"
                        " like “package.name:some/file”.")
    parser.add_argument("--sqlalchemy", metavar="URL",
                        help="Select the SQLAlchemy context. URL is a"
                        " string of the kind “mysql+pymysql://test:test@127.0.0.1/test”.")
    parser.add_argument("--postgresql", metavar="DSN",
                        help="Select the PostgreSQL context. DSN is a string of the kind"
                        " “host=localhost dbname=mydb user=myself password=ouch”.")
    parser.add_argument("--firebird", metavar="DSN",
                        help="Select the Firebird context.")
    parser.add_argument("--sqlite", metavar="DATABASE",
                        help="Select the SQLite context.")
    parser.add_argument("--mysql", metavar="DBNAME",
                        help="Select the MySQL context.")
    parser.add_argument("-u", "--username", metavar="USER",
                        help="Username to log into the database.")
    parser.add_argument("-p", "--password", metavar="PASSWORD",
                        help="Password")
    parser.add_argument("--host", metavar="HOSTNAME", default="localhost",
                        help="Host name where MySQL server runs, defaults to “localhost”.")
    parser.add_argument("--port", metavar="PORT", default=3306, type=int,
                        help="Port number used by the MySQL server, defaults to “3306”.")
    parser.add_argument("--charset", metavar="CHARSET", default="utf8mb4",
                        help="Encoding used by the MySQL driver, defaults to “utf8mb4”.")
    parser.add_argument("--driver", metavar="DRIVER", default="pymysql",
                        help="Driver to access MySQL, defaults to “pymysql”.")
    parser.add_argument("-l", "--log-file", metavar="FILE",
                        dest="log_path",
                        help="Specify where to write the execution log.")
    parser.add_argument("--assume-already-applied", default=False, action="store_true",
                        help="Assume missing patches are already applied, do not"
                        " re-execute them.")
    parser.add_argument("--assert", metavar="NAME", action="append", dest="assertions",
                        help="Introduce an arbitrary assertion usable as a pre-condition"
                        " by the scripts. NAME may be a simple string or something like"
                        " “production=true”. This option may be given multiple times.")
    parser.add_argument("--define", metavar="VAR", action="append", dest="variables",
                        help="Define an arbitrary variable usable as “{{VARNAME}}” within"
                        " a script. VAR must be something like “varname=value”."
                        " This option may be given multiple times.")
    parser.add_argument("-n", "--dry-run", default=False, action="store_true",
                        help="Don't apply patches, just list them.")
    parser.add_argument("-v", "--verbose", default=False, action="store_true",
                        help="Emit noise.")
    parser.add_argument("-d", "--debug", default=False, action="store_true",
                        help="Emit debug messages.")
    parser.add_argument("-b", "--backups-dir", metavar="DIR", default=tempfile.gettempdir(),
                        help="Perform a backup of the database in directory DIR"
                        " (by default “%(default)s”) before doing anything."
                        " Specify “None” to disable backups.")

    args = parser.parse_args()

    if args.log_path:
        level = logging.DEBUG if args.debug else logging.INFO
        logging.basicConfig(filename=args.log_path, level=level,
                            format="%(asctime)s [%(levelname).1s] %(message)s",
                            datefmt="%Y-%m-%d %H:%M:%S")
    else:
        if args.debug:
            level = logging.DEBUG
        elif args.verbose:
            level = logging.INFO
        else:
            level = logging.WARNING
        logging.basicConfig(level=level, format="[%(levelname).1s] %(message)s")

    sqlctx = get_context_from_args(args)
    if sqlctx is None:
        print("You must select exactly one database with either “--postgresql”,"
              " “--firebird”, “--sqlalchemy”, “--mysql” or “--sqlite”!")
        return USAGE

    if args.backups_dir != 'None':
        sqlctx.backup(args.backups_dir)

    try:
        pm = patch_manager(args.storage)
    except DuplicatedScriptError as e:
        print("Error: %s" % e)
        return DATAERR

    if args.assertions:
        try:
            sqlctx.addAssertions(args.assertions)
        except ValueError as e:
            print("Invalid assertion: %s" % e)
            return CONFIG

    if args.variables:
        try:
            sqlctx.addVariables(args.variables)
        except ValueError as e:
            print("Invalid variable: %s" % e)
            return CONFIG

    patches = pm.neededPatches(sqlctx)
    execute = ExecutionContext.execute

    try:
        count = 0
        for p in patches:
            count += 1
            if not args.dry_run:
                execute(p, args)
            else:
                print("I would execute %s... " % p)
        print("\nDone, applied %d script%s" %
              (count, "s" if count != 1 else ""))
        return OK
    except (DependencyError, ExecutionError) as e:
        try:
            print("\nError: %s" % e)
        except:
            import sys
            if sys.version_info.major >= 3:
                print("\nError: %s" % e)
            else:
                print("\nError:", unicode(e).encode('ascii', 'ignore'))
        return SOFTWARE


if __name__ == '__main__':
    from sys import exit

    exit(main())
