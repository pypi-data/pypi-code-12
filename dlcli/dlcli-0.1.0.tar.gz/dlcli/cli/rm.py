from ..cli import *
import click
import logging

from ..api import accounts as accounts_api
from ..api import agents as agents_api
from ..api import dashboards as dashboards_api
from ..api import links as links_api
from ..api import orgs as orgs_api
from ..api import plugins as plugins_api
from ..api import rules as rules_api
from ..api import tags as tags_api
from ..api import metrics as metrics_api
from ..api import series as series_api
from ..api import user as user_api

logger = logging.getLogger(__name__)


@cli.group('rm')
def rm():
    """deletes things"""


@click.command(short_help="rm account")
@click.argument('account')
def account(account):
    click.confirm(
        'Once you delete an account, there is no going back. Are you sure?',
        abort=True)
    context.settings['account'] = account
    resp = accounts_api.delete_account(**context.settings)
    if resp.status_code == 204:
        click.echo('Deleted account ' + account)
    else:
        click.echo('Error deleting ' + account + '. Status Code: ' + click.style(str(resp.status_code), fg='red'))


@click.command(short_help="rm agent")
@click.argument('agent')
def agent(agent):
    resp = agents_api.delete_agent(agent=agent, **context.settings)
    if resp.status_code == 204:
        click.echo('Deleted agent ' + agent)
    else:
        click.echo('Error deleting ' + agent + '. Status Code: ' + click.style(
            str(resp.status_code),
            fg='red'))


@click.command(short_help="rm dashboard")
@click.argument('dashboard')
def dashboard(dashboard):
    resp = dashboards_api.delete_dashboard(dashboard=dashboard, **context.settings)
    if resp.status_code == 204:
        click.echo('Deleted dashboard ' + dashboard)
    else:
        click.echo('Error deleting ' + dashboard + '. Status Code: ' +
                   click.style(
                       str(resp.status_code),
                       fg='red'))


@click.command(short_help="rm link")
@click.argument('link')
def link(link):
    resp = links_api.delete_link(link=link, **context.settings)
    if resp.status_code == 204:
        click.echo('Deleted link ' + link)
    else:
        click.echo('Error deleting ' + link + '. Status Code: ' + click.style(
            str(resp.status_code),
            fg='red'))


@click.command(short_help="rm org")
@click.argument('org')
def org(org):
    click.confirm(
        'Once you delete an organization, there is no going back. Are you sure?',
        abort=True)
    context.settings['org'] = org
    resp = orgs_api.delete_org(**context.settings)
    if resp.status_code == 204:
        click.echo('Deleted org ' + org)
    else:
        click.echo('Error deleting ' + org + '. Status Code: ' + click.style(
            str(resp.status_code),
            fg='red'))


@click.command(short_help="rm plugin")
@click.argument('plugin')
def plugin(plugin):
    resp = plugins_api.delete_plugin(plugin=plugin, **context.settings)
    if resp.status_code == 204:
        click.echo('Deleted plugin ' + plugin)
    else:
        click.echo('Error deleting ' + plugin + '. Status Code: ' +
                   click.style(
                       str(resp.status_code),
                       fg='red'))


@click.command(short_help="rm rule")
@click.argument('rule')
def rule(rule):
    resp = rules_api.delete_rule(rule=rule, **context.settings)
    if resp.status_code == 204:
        click.echo('Deleted rule ' + rule)
    else:
        click.echo('Error deleting ' + rule + '. Status Code: ' + click.style(
            str(resp.status_code),
            fg='red'))


@click.command(short_help="rm tag")
@click.argument('tag')
def tag(tag):
    resp = tags_api.delete_tag(tag=tag, **context.settings)
    if resp.status_code == 204:
        click.echo('Deleted tag ' + tag)
    else:
        click.echo('Error deleting ' + tag + '. Status Code: ' + click.style(
            str(resp.status_code),
            fg='red'))


@click.command(short_help="rm token")
@click.argument('name')
def token(ctx, name):
    resp = user_api.delete_user_token(token_name=name, **context.settings)
    if resp.status_code == 204:
        click.echo('Deleted token ' + name)
    else:
        click.echo('Error deleting ' + name + '. Status Code: ' + click.style(
            str(resp.status_code),
            fg='red'))


rm.add_command(account)
rm.add_command(agent)
rm.add_command(dashboard)
rm.add_command(link)
rm.add_command(org)
rm.add_command(plugin)
rm.add_command(rule)
rm.add_command(tag)
rm.add_command(token)
