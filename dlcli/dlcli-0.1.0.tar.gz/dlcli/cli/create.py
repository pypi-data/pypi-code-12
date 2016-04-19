from ..cli import *
import click
import logging
import context

from ..api import user as user_api

logger = logging.getLogger(__name__)


@cli.group('create')
def create():
    """creates things"""


@click.command(short_help="Create token")
@click.argument('name')
def token(name):
    try:
        print user_api.create_user_token(token_name=name, **context.settings)['token']
    except Exception, e:
        print "token creation failed. is the name already taken?: %s" % e


create.add_command(token)
