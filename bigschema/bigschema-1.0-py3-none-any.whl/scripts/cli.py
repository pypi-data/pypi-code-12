from __future__ import print_function, unicode_literals
from pathlib import Path

import click

from bigschema.workflow import LOG
from bigschema.workflow import workflow

try:
    import ujson as json
except ImportError as e:
    import json

__author__ = "danishabdullah"

help_text = """BigQuery schema generation tool.

This is very simple command line tool that takes a source yaml file,
an optional destination directory default is ./schema/ and an output
format and transforms the given yaml specifications to BigQuery compliant
schema in the desired output format.

YAML File Specification

-----------------------

spec-mode: "compact" | "verbose"

---------------------------------------------------------------------

spec-mode: "verbose"

--------------------

table:

  type: "table"

  fields:

    - name:

      type: "integer" | "float" | "string" | "timestamp" | "bytes" | "record_name"

      mode: "nullable" | "repeated" | "required"

record:

  type: "record"

  fields:

    - name:

      type: "integer" | "float" | "string" | "timestamp" | "bytes" | "record_name"

      mode: "nullable" | "repeated" | "required"


----------------------------------------------------------------------

spec-mode: "compact"

--------------------

table:

  type: table

  fields:

    - name_of_column, type_of_column, mode_of_column

record:

  type: record

  fields:

    - name_of_column, type_of_column, mode_of_column
"""


@click.command(help=help_text)
@click.argument('source', type=click.Path(exists=True), )
@click.argument('destination', type=click.Path(exists=True), default='./schemas/')
@click.option('--output-format', '-f', default="json", type=click.Choice(["java", "json"]),
              help="Which format to output the data in? Default is JSON")
@click.option('--overwrite', "-o", default=False, type=bool,
              help="Should we overwrite the data in existing file? Default is FALSE")
def cli(source, destination, output_format, overwrite):
    msg = ("Invoked transformation with the following options:\n"
           "\tsource = {},\n\tdestination = {},\n\toutput-format = {}"
           "".format(source, destination, output_format))
    output_format = output_format.lower()
    LOG.info(msg)
    output = workflow(source, output_format)
    path = Path(destination)
    if overwrite or path.is_file():
        if click.confirm("Given destination is a file. This operation will overwrite the contents of the file."
                         "Do you want to continue?", abort=True):
            res = "\n".join([v for v in output.values()])
            with open(destination, 'w') as file:
                LOG.info("Writing output to {}".format(destination))
                file.write(res)
    if path.is_dir():
        for k, v in output.items():
            fp = path / "{}.{}".format(k, output_format)
            if fp.exists() and not overwrite:
                if click.confirm("Are you sure you want to overwrite existing files?", abort=True):
                    overwrite = True
            fp = fp.as_posix()
            with open(fp, 'w') as file:
                LOG.info("Writing output to {}".format(fp))
                file.write(v)
