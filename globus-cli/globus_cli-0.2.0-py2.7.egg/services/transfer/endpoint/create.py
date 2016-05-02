from __future__ import print_function
import click

from globus_cli.helpers import (
    CaseInsensitiveChoice, common_options, print_json_response)
from globus_cli.services.transfer.helpers import (
    get_client, assemble_generic_doc)
from globus_cli.services.transfer.endpoint.helpers import (
    create_and_update_opts)


@click.command('create', help='Create a new Endpoint')
@common_options
@create_and_update_opts(create=True)
@click.option('--endpoint-type', required=True,
              help=('Type of endpoint to create. "gcp" and "gcs" are just '
                    'shorthand for "globus-connect-personal" and '
                    '"globus-connect-server", respectively'),
              type=CaseInsensitiveChoice((
                  'globus-connect-server', 'globus-connect-personal',
                  's3', 'gcp', 'gcs')))
def endpoint_create(endpoint_type, display_name, description, organization,
                    contact_email, contact_info, info_link, public,
                    default_directory, force_encryption, oauth_server,
                    myproxy_server, myproxy_dn):
    """
    Executor for `globus transfer endpoint create`
    """
    ep_doc = assemble_generic_doc(
        'endpoint',
        display_name=display_name, description=description,
        organization=organization, contact_email=contact_email,
        contact_info=contact_info, info_link=info_link,
        force_encryption=force_encryption, public=public,
        default_directory=default_directory,
        myproxy_server=myproxy_server, myproxy_dn=myproxy_dn,
        oauth_server=oauth_server)
    if endpoint_type == 's3':
        raise NotImplementedError(
            'S3 Endpoints cannot be created through the new CLI yet.')
    elif endpoint_type in ('globus-connect-personal', 'gcp'):
        ep_doc['is_globus_connect'] = True
    elif endpoint_type in ('globus-connect-server', 'gcs'):
        pass

    client = get_client()
    res = client.create_endpoint(ep_doc)
    print_json_response(res)
