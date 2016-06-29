import click
import json
import csv

from client import HubApiClient


def get_api_client(url, token):
    return HubApiClient(
        api_url=url,
        auth_token=token
    )


@click.option(
    '--csv', type=click.File('rb'),
    help=('CSV file with columns for the endpoint'))
@click.option(
    '--json', type=click.File('rb'),
    help=('JSON objects, one per line for the endpoint'))
@click.pass_context
def registrations_import(ctx, csv, json):
    """ Import registrations to the hub service.
    """
    if not any((csv, json)):
        raise click.UsageError("Please specify either --csv or --json.")
    api = get_api_client(ctx.obj.hub.api_url, ctx.obj.hub.token)
    if csv:
        for registration in registrations_from_csv(csv):
            api.create_registration(registration)
    if json:
        for registration in registrations_from_json(json):
            api.create_registration(registration)
    click.echo("Completed importing registrations.")


def registrations_from_csv(csv_file):
    reader = csv.DictReader(csv_file)
    for data in reader:
        registration = {
            "mother_id": data["mother_id"],
            "stage": data["stage"],
            "data": {}
        }
        for key, value in data.iteritems():
            if key not in ("mother_id", "stage"):
                registration["data"][key] = value
        yield registration


def registrations_from_json(json_file):
    for line in json_file:
        data = json.loads(line.rstrip("\n"))
        if not isinstance(data, dict):
            raise click.UsageError(
                "JSON file lines must be objects.")
        yield data
