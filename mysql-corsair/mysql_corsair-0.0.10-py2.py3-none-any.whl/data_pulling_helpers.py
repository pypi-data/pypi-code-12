import re
import logging
import subprocess
import tempfile


logger = logging.getLogger(__name__)


MYSQL_IGNORED_WARNINGS = (
    re.compile(r"Warning: Using a password on the command line interface can be insecure\."),
    re.compile(r"ERROR 1062 \(23000\) at line \d+: Duplicate entry '.+' for key 'PRIMARY'"),
)


def _call_mysql(*args, **kwargs):
    kwargs.setdefault('stderr', subprocess.PIPE)
    proc = subprocess.Popen(*args, **kwargs)
    stdout, stderr = proc.communicate()
    for line in stderr.split('\n'):
        if line and not any(w.match(line) for w in MYSQL_IGNORED_WARNINGS):
            logger.warning(line)
    return proc.returncode


def _mysqldump_command(table_name, where_clause, dumpfile,
                       conn_dict, overwrite):
    cmd = [
        'mysqldump', conn_dict['db'], table_name,
        '--where={0}'.format(where_clause),
        '--user={user}'.format(**conn_dict),
        '--password={passwd}'.format(**conn_dict),
        '--host={host}'.format(**conn_dict),
        '--port={port}'.format(**conn_dict),
        '--lock-tables=false',
        '--insert-ignore',
    ]
    logger.debug("mysqldump command for table {0}: {1}".format(
        table_name, cmd)
    )
    if not overwrite:
        cmd.append("--no-create-info")
    _call_mysql(cmd, stdout=dumpfile)


def _mysql_command(dumpfile, conn_dict):
    cmd = [
        'mysql', conn_dict['db'],
        '--user={user}'.format(**conn_dict),
        '--password={passwd}'.format(**conn_dict),
        '--host={host}'.format(**conn_dict),
        '--port={port}'.format(**conn_dict),
        '--force',
    ]
    _call_mysql(cmd, stdin=dumpfile)


def get_from_source_and_write_to_target(table_name, where_clause,
                                        source_conn_dict, target_conn_dict,
                                        overwrite):
    if len(where_clause) > 200000:
        logger.info(
            """
            Not pulling data from table {0}, because there are too many values
            in the WHERE clause.
            """.format(table_name)
        )
    else:
        with tempfile.NamedTemporaryFile() as dumpfile_stream:
            _mysqldump_command(
                table_name, where_clause, dumpfile_stream, source_conn_dict,
                overwrite
            )
            dumpfile_stream.seek(0)
            _mysql_command(dumpfile_stream, target_conn_dict)
