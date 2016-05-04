from __future__ import print_function
import click

from globus_cli.helpers import (
    outformat_is_json, common_options, print_json_response)
from globus_cli.services.transfer.helpers import (
    get_client, assemble_generic_doc, endpoint_id_option)
from globus_cli.services.transfer.endpoint.helpers import (
    create_and_update_opts)


@click.command('update', help='Update attributes of an Endpoint')
@common_options
@create_and_update_opts(create=False)
@endpoint_id_option
def endpoint_update(endpoint_id, display_name, description, organization,
                    contact_email, contact_info, info_link, public,
                    default_directory, force_encryption, oauth_server,
                    myproxy_server, myproxy_dn):
    """
    Executor for `globus transfer endpoint update`
    """
    client = get_client()

    ep_doc = assemble_generic_doc(
        'endpoint',
        display_name=display_name, description=description,
        organization=organization, contact_email=contact_email,
        contact_info=contact_info, info_link=info_link,
        force_encryption=force_encryption, public=public,
        default_directory=default_directory,
        myproxy_server=myproxy_server, myproxy_dn=myproxy_dn,
        oauth_server=oauth_server)

    res = client.update_endpoint(endpoint_id, ep_doc)

    if outformat_is_json():
        print_json_response(res)
    else:
        print(res['message'])
