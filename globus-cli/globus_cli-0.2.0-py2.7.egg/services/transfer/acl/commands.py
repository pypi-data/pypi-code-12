import click

from globus_cli.helpers import common_options

from globus_cli.services.transfer.acl.list import acl_list
from globus_cli.services.transfer.acl.add_rule import add_acl_rule
from globus_cli.services.transfer.acl.update_rule import update_acl_rule
from globus_cli.services.transfer.acl.del_rule import del_acl_rule


@click.group(name='acl', help='Manage Endpoint Access Control Lists')
@common_options
def acl_command():
    pass


acl_command.add_command(acl_list)
acl_command.add_command(add_acl_rule)
acl_command.add_command(update_acl_rule)
acl_command.add_command(del_acl_rule)
