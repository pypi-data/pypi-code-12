# -*- coding: utf-8 -*-
from .app import app
import click


@click.command()
@click.argument('path', default='.', type=click.Path(exists=True,
                                                     file_okay=False,
                                                     writable=True))
@click.option('--port', default=5000)
@click.option('--host', default='127.0.0.1')
def run(path, port, host):
    app.config['DEBUG'] = True
    app.config['NOTES_DIR'] = path
    app.config['SECRET_KEY'] = 'bMYruZ0WbDsJeZI7K6SSZRDgNKCaKsGi'
    app.run(host=host, port=port, use_reloader=False)
