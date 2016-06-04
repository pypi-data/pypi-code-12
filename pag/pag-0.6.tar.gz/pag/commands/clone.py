import click

from pag.app import app
from pag.utils import (
    repo_url,
    run,
)

@app.command()
@click.argument('name')
def clone(name):
    url = repo_url(name, ssh=True, git=True)
    run(['git', 'clone', url, name.split('/')[-1]])
