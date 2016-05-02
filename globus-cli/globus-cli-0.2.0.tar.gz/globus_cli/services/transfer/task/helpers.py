import click


def task_id_option(help='ID of the Task'):
    def inner_decorator(f):
        f = click.option('--task-id', required=True, help=help)(f)
        return f
    return inner_decorator
