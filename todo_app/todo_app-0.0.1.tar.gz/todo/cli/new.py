import click
from todo.todo import TodoMananger


@click.command()
@click.option('-nt', default=None, help='notebook name')
@click.option('-t', help='the name of the todo item')
def cli(t, nt=None):
    todo = TodoMananger()
    todo.add_item(t, notebook=nt)
