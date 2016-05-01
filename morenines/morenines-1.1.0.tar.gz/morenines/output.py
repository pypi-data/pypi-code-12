import click

GOOD_COLOR = 'green'
WARN_COLOR = 'yellow'
BAD_COLOR = 'red'
IGNORED_COLOR = 'blue'

def set_output_color(color):
    # Print nothing except the ANSI escape sequence
    click.secho('', nl=False, fg=color, reset=False)


def clear_output_color():
    # Print nothing except the reset escape sequence
    click.secho('', nl=False, reset=True)


def output(message, color=None, items=[]):
    if color:
        set_output_color(color)

    click.echo(message)

    for item in sorted(items):
        click.echo("  {}".format(item))

    clear_output_color()

def info(message, items=[]):
    output(message, None, items)

def success(message, items=[]):
    output("SUCCESS: {}".format(message), GOOD_COLOR, items)

def warning(message, items=[]):
    output("WARNING: {}".format(message), WARN_COLOR, items)


def error(message, items=[]):
    output("ERROR: {}".format(message), BAD_COLOR, items)

def print_filelists(new_files, changed_files, missing_files, ignored_files):
    if not any([new_files, changed_files, missing_files, ignored_files]):
        output("Index is up-to-date (no changes)", GOOD_COLOR)
        return

    if new_files:
        output("New files (not in index):", WARN_COLOR, new_files)

        # Print a blank space between sections
        if missing_files or changed_files or ignored_files:
            click.echo()

    if missing_files:
        output("Missing files:", WARN_COLOR, missing_files)

        # Print a blank space between sections
        if changed_files or ignored_files:
            click.echo()

    if changed_files:
        output("Changed files (hash differs from index):", BAD_COLOR, changed_files)

        # Print a blank space between sections
        if ignored_files:
            click.echo()

    if ignored_files:
        output("Ignored files and directories:", IGNORED_COLOR, ignored_files)
