from __future__ import print_function
import click
import click_config

import seed_services_cli.identity_store
import seed_services_cli.stage_based_messaging
import seed_services_cli.hub


class config(object):
    class hub(object):
        api_url = 'http://hub.fqdn/api/v1'
        token = 'REPLACEME'

    class identity_store(object):
        api_url = 'http://id.example.org/api/v1'
        token = 'REPLACEME'

    class stage_based_messaging(object):
        api_url = 'http://sbm.example.org/api/v1'
        token = 'REPLACEME'


@click.group(name="seed-services-cli")
@click.version_option()
@click_config.wrap(module=config, sections=('hub', 'identity_store',
                   'stage_based_messaging'))
@click.pass_context
def cli(ctx):
    """ Seed Services command line utility. """
    ctx.obj = config

cli.command('identity-search')(seed_services_cli.identity_store.search)
cli.command('identity-get')(seed_services_cli.identity_store.get_identity)
cli.command('identity-import')(seed_services_cli.identity_store.identities_import)  # noqa
cli.command('sbm-schedules')(seed_services_cli.stage_based_messaging.schedules)
cli.command('sbm-messagesets')(seed_services_cli.stage_based_messaging.messagesets)  # noqa
cli.command('sbm-messages')(seed_services_cli.stage_based_messaging.messages)
cli.command('sbm-messages-delete')(seed_services_cli.stage_based_messaging.messages_delete)  # noqa
cli.command('sbm-messages-import')(seed_services_cli.stage_based_messaging.messages_import)  # noqa
cli.command('hub-registrations-import')(seed_services_cli.hub.registrations_import)  # noqa
