###########################################################################
#          (C) Vrije Universiteit, Amsterdam (the Netherlands)            #
#                                                                         #
# This file is part of AmCAT - The Amsterdam Content Analysis Toolkit     #
#                                                                         #
# AmCAT is free software: you can redistribute it and/or modify it under  #
# the terms of the GNU Affero General Public License as published by the  #
# Free Software Foundation, either version 3 of the License, or (at your  #
# option) any later version.                                              #
#                                                                         #
# AmCAT is distributed in the hope that it will be useful, but WITHOUT    #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or   #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public     #
# License for more details.                                               #
#                                                                         #
# You should have received a copy of the GNU Affero General Public        #
# License along with AmCAT.  If not, see <http://www.gnu.org/licenses/>.  #
###########################################################################
import functools
import re
import io
import struct
import subprocess
import itertools
import tempfile
import datetime
import collections
import os.path
import logging

from threading import Thread

from exportable.columns import Column
from exportable.exporters.base import Exporter
from exportable.table import Table

log = logging.getLogger(__name__)

# Do not let PSPP documentation get in the way of writing proper PSPP input :)
MAX_STRING_LENGTH = 2**15 - 1  # PSPP Maximum per: http://bit.ly/1SVPNfU

PSPP_TYPES = {
    int: "F8.0",
    str: "A{}".format(MAX_STRING_LENGTH),
    float: "DOT9.2",
    datetime.datetime: "DATETIME20"
}

PSPP_COMMANDS = r"""
GET DATA
    /type=txt
    /file="{infile}"
    /encoding="utf-8"
    /arrangement=delimited
    /delimiters="\t"
    /qualifier=""
    /variables {variables}.
SAVE
    /compressed
    /outfile='{outfile}'.
"""

PSPP_VERSION_RE = re.compile(b"pspp \(GNU PSPP\) (\d+)\.(\d+).(\d+)")
PSPPVersion = collections.namedtuple("PSPPVersion", ["major", "minor", "micro"])

class PSPPError(Exception):
    pass


def get_pspp_version() -> PSPPVersion:
    try:
        process = subprocess.Popen(["pspp", "--version"], stdout=subprocess.PIPE)
    except FileNotFoundError:
        raise FileNotFoundError("Could not execute pspp. Is it installed?")

    stdout, _ = process.communicate()
    for line in stdout.splitlines():
        match = PSPP_VERSION_RE.match(line)
        if match:
            return PSPPVersion(*map(int, match.groups()))

    raise PSPPError("Could not find version of installed pspp.")


def get_var_name(col: Column, seen: set):
    fn = col.label.replace(" ", "_")
    fn = fn.replace("-", "_")
    fn = re.sub('[^a-zA-Z_]+', '', fn)
    fn = re.sub('^_+', '', fn)
    fn = fn[:16]
    if fn in seen:
        for i in itertools.count():
            if "%s_%i" % (fn, i) not in seen:
                fn = "%s_%i" % (fn, i)
                break
    seen.add(fn)
    return fn


@functools.lru_cache(maxsize=128)
def get_pspp_commands(table: Table, outfile: str, infile="/dev/null") -> bytes:
    # Deduce cleaned variable names and variable types
    seen = set()
    varnames = {col: get_var_name(col, seen) for col in table.columns}
    variables = [(varnames[col], PSPP_TYPES[col.type]) for col in table.columns]
    variables = " ".join(map(str, itertools.chain.from_iterable(variables)))
    commands = PSPP_COMMANDS.format(infile=infile, outfile=outfile, variables=variables)
    return commands.encode()


def chunkify(it, size=0):
    if not size:
        return it

    filler = object()
    iters = [iter(it)] * size

    for chunk in itertools.zip_longest(*iters, fillvalue=filler):
        yield (value for value in chunk if value is not filler)


def exec_pspp(commands: bytes):
    """Executes PSPP with given commands as input (through stdin)."""
    log.debug("Starting PSPP")
    pspp = subprocess.Popen(
        ["pspp", "-b"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    log.debug("Sending code to pspp..")
    stdout, stderr = pspp.communicate(input=commands)

    stdout = stdout.decode()
    stderr = stderr.decode()

    log.debug("PSPP stderr: %s" % stderr)
    log.debug("PSPP stdout: %s" % stdout)

    stderr = stderr.replace('pspp: error creating "pspp.jnl": Permission denied', '')
    stdout = stdout.replace('pspp: ascii: opening output file "pspp.list": Permission denied', '')

    if stderr.strip():
        raise PSPPError(stderr)
    if "error:" in stdout.lower():
        raise PSPPError("PSPP Exited with error: \n\n%s" % stdout)


def copyfileobj(fsrc, fdst, length=16*1024, skip_first=0):
    """Copy of shutil.copyfileobj, with added 'skip_first' parameter."""
    fsrc.read(skip_first)
    while 1:
        buf = fsrc.read(length)
        if not buf:
            break
        fdst.write(buf)


def serialize_str(s):
    return s.replace('\n', ". ").replace("\r", "").replace("\t", " ")[:MAX_STRING_LENGTH]


def serialize_datetime(timestamp):
    return timestamp.strftime("%d-%b-%Y-%H:%M:%S").upper()


def serialize_date(date):
    return serialize_datetime(datetime.datetime(date.year, date.month, date.day))


def get_serializer(column):
    if column.type == str:
        return serialize_str
    elif column.type in (int, float):
        return str
    elif column.type == datetime.datetime:
        return serialize_datetime
    elif column.type == datetime.date:
        return serialize_date
    else:
        raise ValueError("Did not recognize serializer type for: {}".format(column))


def write_data(table: Table, rows, fp):
    serializers = list(map(get_serializer, table.columns))
    for row in rows:
        for serializer, value in zip(serializers, row):
            if value is not None:
                fp.write(serializer(value).encode())
            fp.write(b"\t")
        fp.write(b"\n")
    fp.close()


def write_table(table, fp, chunksize=1000):
    """
    Write a given table to a file like object. Depending on the chunk size, this function will not
    load all rows of the table in memory at once.

    @param table: table to serialize to a SPSS system file
    @param fp: file like object to write to
    @param chunksize: if 0, do not use chunks (keeps every row in memory!)
    """
    log.debug("Check if we've got the right version of PSPP installed")
    version = get_pspp_version()
    if version < PSPPVersion(0, 8, 5):
        raise PSPPVersion("Expected pspp>=8.5.0, but found {}".format(version))

    # Create fifos
    tmp_dir = tempfile.mkdtemp(prefix="amcat-pspp-")
    fifo_in = os.path.join(tmp_dir, "in.txt")
    fifo_out = os.path.join(tmp_dir, "out.sav")
    os.mkfifo(fifo_in)
    os.mkfifo(fifo_out)

    try:
        # Prepare buffer for header
        header_buffer = io.BytesIO()
        out_copy_target = lambda: copyfileobj(open(fifo_out, "rb"), header_buffer)
        out_copy_thread = Thread(target=out_copy_target)
        out_copy_thread.start()

        # Execute PSPP
        exec_pspp(get_pspp_commands(table, fifo_out))

        # Wait for copying to finish
        out_copy_thread.join()

        # Write expected number of rows to header
        header_buffer.seek(0x50)
        header_buffer.write(struct.pack("<i", len(table)))
        header_buffer.seek(0)
        copyfileobj(header_buffer, fp)

        # Determine header length
        header_length = len(header_buffer.getvalue())

        # Write data in chunks
        for chunk in chunkify(table.rows, size=chunksize):
            # PSPP outfile -> caller buffer. We skip writing the header, only data.
            out_copy_target = lambda: copyfileobj(open(fifo_out, "rb"), fp, skip_first=header_length)
            out_copy_thread = Thread(target=out_copy_target)
            out_copy_thread.start()

            # Table row chunk -> PSPP
            in_copy_target = lambda: write_data(table, chunk, open(fifo_in, "wb"))
            in_copy_thread = Thread(target=in_copy_target)
            in_copy_thread.start()

            # let PSPP generate data for given chunk
            exec_pspp(get_pspp_commands(table, fifo_out, fifo_in))

            out_copy_thread.join()
            in_copy_thread.join()

    finally:
        os.unlink(fifo_in)
        os.unlink(fifo_out)
        os.removedirs(tmp_dir)


class SPSSExporter(Exporter):
    extension = "sav"
    content_type = "application/x-spss-sav"

    def dump(self, table, fo, filename_hint=None, encoding_hint="utf-8"):
        write_table(table, fo)

