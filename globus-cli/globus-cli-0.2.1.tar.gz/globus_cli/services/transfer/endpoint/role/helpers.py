import click


def role_id_option(f):
    f = click.option('--role-id', required=True, help='ID of the Role')(f)
    return f
