#! /usr/bin/env python3
"""
Click-based command-line interface written in Python 3 that takes a CSV
file and outputs a bar chart. The heavy-lifting is done by
:func:`agate.Table.print_bars`.
"""
import io
import warnings

import agate
import click


class Number(click.ParamType):

    """
    Declares a parameter to be a numeric value. The value will be
    provided as an :class:`int` if the string is all numbers, else a
    :class:`float`.
    """

    name = "number"

    def __repr__(self):
        return self.name.upper().replace(" ", "_")

    def convert(self, value, param, ctx):
        """
        Converts the parameter value to an :class:`int` if the string is
        all numbers, else a :class:`float`. If conversion to a
        :class:`float` fails, an exception is raised.
        """
        if value.isdigit():
            value = int(value)
        else:
            try:
                value = float(value)
            except ValueError:
                self.fail("'{}' is not a valid number.".format(value))
        return value


@click.command()
@click.option("--label", help="Name or index of the column containing the "
                              "label values. Defaults to the first text "
                              "column.")
@click.option("--value", help="Name or index of the column containing the bar "
                              "values. Defaults to the first numeric column.")
@click.option("--domain", help="Minimum and maximum values for the chart's "
                               "x-axis.", nargs=2, type=Number())
@click.option("--width", help="Width, in characters, to use to print the "
                              "chart.", default=click.get_terminal_size()[0],
                              show_default=True, type=click.INT)
@click.option("--skip", help="Number of rows to skip.", type=click.INT,
              default=0, show_default=True)
@click.option("--encoding", help="Character encoding of the CSV file.",
              default="UTF-8", show_default=True)
@click.option("--no-header", help="Indicates the CSV file contains no header "
                                  "row.", is_flag=True, default=False)
@click.option("--printable", help="Only use printable characters to draw the "
                                  "bar chart.", is_flag=True, default=False)
@click.argument("csv", type=click.File("rt"))
def main(label, value, domain, width, skip, encoding, no_header, printable,
         csv):
    """
    Load a CSV file and output a bar chart.
    """
    # Ensure ``SIGPIPE`` doesn't throw an exception. This prevents the
    # ``[Errno 32] Broken pipe`` error you see when, e.g., piping to ``head``.
    # For details see http://bugs.python.org/issue1652.
    try:
        import signal
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    except (ImportError, AttributeError):
        # Do nothing on platforms without signals or ``SIGPIPE``.
        pass

    # Load the CSV into an ``agate`` table. Catch warnings so a RuntimeError
    # doesn't get displayed when there are no column names (that is, when
    # ``header=False``).
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            table = agate.Table.from_csv(csv, skip_lines=skip,
                                         header=(not no_header),
                                         encoding=encoding)
        except UnicodeDecodeError:
            raise click.BadParameter("file not encoded as {}".format(encoding),
                                     param_hint="CSV")
        except ValueError:
            raise click.BadParameter("not a valid CSV file", param_hint="CSV")

    # Parse the label. Possibilities are that it's a string that matches a
    # column name, that it's a column index (1 being the first column), or that
    # it's blank --- in which case the first text column is used, if there is
    # one.
    if label and label.isdigit():
        label = int(label)
        try:
            label = table.columns[label + 1]
        except IndexError:
            raise click.UsageError("index {} is beyond the last column, '{}', "
                                   "at index {}".format(label,
                                                        table.columns[-1].name,
                                                        len(table.columns)))
    elif label is None:
        try:
            label = [c.name for c in table.columns
                     if isinstance(c.data_type, agate.Text)][0]
        except IndexError:
            raise click.UsageError("no --label specified and no text column "
                                   "found")
    else:
        # Check that there's a column with the given name.
        try:
            table.columns[label]
        except KeyError:
            raise click.BadParameter("no column named '{}'".format(label),
                                     param_hint="label")

    # Parse the value. Possibilities are that it's a string that matches a
    # column name, that it's a column index (1 being the first column), or that
    # it's blank --- in which case the first numeric column is used, if there
    # is one.
    if value and value.isdigit():
        value = int(value)
        try:
            value = table.columns[value + 1]
        except IndexError:
            raise click.UsageError("index {} is beyond the last column, '{}', "
                                   "at index {}".format(value,
                                                        table.columns[-1].name,
                                                        len(table.columns)))
    elif value is None:
        try:
            value = [c.name for c in table.columns
                     if isinstance(c.data_type, agate.Number)][0]
        except IndexError:
            raise click.UsageError("no --value specified and no number column "
                                   "found")
    else:
        # Check that there's a column with the given name.
        try:
            table.columns[value]
        except KeyError:
            raise click.BadParameter("no column named '{}'".format(value),
                                     param_hint="value")

    with io.StringIO() as fh:
        table.print_bars(label, value, domain, width, fh, printable=printable)
        fh.seek(0)
        click.echo(fh.read())


if __name__ == "__main__":
    main()
