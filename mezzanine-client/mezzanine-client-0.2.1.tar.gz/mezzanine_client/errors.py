import click


class MezzanineCLIError(click.ClickException):
    """
    Base error class for Mezzanine API CLI.
    """

    def show(self, file=None):
        click.secho('Error: {}'.format(self.format_message()), file=file, fg='red', bg=None, bold=True)


class MezzanineValueError(ValueError):
    """
    Error indicating that user input data was invalid.
    """
