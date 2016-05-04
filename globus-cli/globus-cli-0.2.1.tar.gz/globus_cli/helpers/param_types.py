import click


class CaseInsensitiveChoice(click.Choice):
    def convert(self, value, param, ctx):
        if value is None:
            return None
        return super(CaseInsensitiveChoice, self).convert(
            value.lower(), param, ctx)
