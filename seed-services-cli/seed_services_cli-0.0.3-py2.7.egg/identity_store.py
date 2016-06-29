import click
import json
import csv

from client import IdentityStoreApiClient
from demands import HTTPServiceError


def get_api_client(url, token):
    return IdentityStoreApiClient(
        api_url=url,
        auth_token=token
    )


@click.option(
    '--address_type', '-t',
    help='Address Type (e.g. msisdn)')
@click.option(
    '--address', '-a',
    help='Address (e.g. 27812345678)')
@click.pass_context
def search(ctx, address_type, address):
    """ Find an identity
    """
    api = get_api_client(ctx.obj.identity_store.api_url,
                         ctx.obj.identity_store.token)
    if not all((address_type, address)):
        raise click.UsageError(
            "Please specify address type and address. See --help.")
    click.echo("Looking for %s of %s." % (address_type, address))
    results = api.get_identity_by_address(address_type, address)
    click.echo("Found %s results:" % results["count"])
    if results["count"] > 0:
        for result in results["results"]:
            click.echo(result["id"])


@click.option(
    '--identity', '-i',
    help='Identity UUID')
@click.pass_context
def get_identity(ctx, identity):
    """ Find a specific identity
    """
    api = get_api_client(ctx.obj.identity_store.api_url,
                         ctx.obj.identity_store.token)
    if identity:
        # get a very particular identity
        try:
            result = api.get_identity(identity_id=identity)
        except HTTPServiceError:
            click.echo("Identity not found")
            ctx.abort()
    else:
        raise click.UsageError(
            "Please specify identity UUID. See --help.")
    click.echo(json.dumps(result))


@click.option(
    '--csv', type=click.File('rb'),
    help=('CSV file with columns for the endpoint'))
@click.option(
    '--json', type=click.File('rb'),
    help=('JSON objects, one per line for the endpoint'))
@click.pass_context
def identities_import(ctx, csv, json):
    """ Import to the Identity Store service.
    """
    if not any((csv, json)):
        raise click.UsageError("Please specify either --csv or --json.")
    api = get_api_client(ctx.obj.identity_store.api_url,
                         ctx.obj.identity_store.token)
    if csv:
        for identity in identities_from_csv(csv):
            api.create_identity(identity)
    if json:
        for identity in identities_from_json(json):
            api.create_identity(identity)
    click.echo("Completed importing identities.")


def identities_from_csv(csv_file):
    reader = csv.DictReader(csv_file)
    for data in reader:
        identity = {
            "communicate_through": data["communicate_through"],
            "details": {
                "addresses": {
                    data["address_type"]: data["address"]
                },
                "default_addr_type": data["address_type"]
            }
        }
        for key, value in data.iteritems():
            if key not in ("address_type", "address", "communicate_through"):
                identity["details"][key] = value
        yield identity


def identities_from_json(json_file):
    for line in json_file:
        data = json.loads(line.rstrip("\n"))
        if not isinstance(data, dict):
            raise click.UsageError(
                "JSON file lines must be objects.")
        yield data
