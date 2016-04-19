import datetime
import os
import re

import click

import requests
import tarfile
import tempfile
import time
import zign.api
from clickclick import error, AliasedGroup, print_table, OutputFormat, UrlType

from .api import docker_login, request, get_latest_tag, DockerImage
import pierone
import stups_cli.config


KEYRING_KEY = 'pierone'

CONTEXT_SETTINGS = {'help_option_names': ['-h', '--help']}

output_option = click.option('-o', '--output', type=click.Choice(['text', 'json', 'tsv']), default='text',
                             help='Use alternative output format')

url_option = click.option('--url', help='Pier One URL', metavar='URI')

TEAM_PATTERN_STR = r'[a-z][a-z0-9-]+'
TEAM_PATTERN = re.compile(r'^{}$'.format(TEAM_PATTERN_STR))


def validate_team(ctx, param, value):
    if not TEAM_PATTERN.match(value):
        msg = 'Team ID must satisfy regular expression pattern "{}"'.format(TEAM_PATTERN_STR)
        raise click.BadParameter(msg)
    return value


def parse_time(s: str) -> float:
    '''
    >>> parse_time('foo')
    time data 'foo' does not match format '%Y-%m-%dT%H:%M:%S.%fZ'
    >>> parse_time('2015-04-14T19:09:01.000Z') > 0
    True
    '''
    try:
        utc = datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%S.%fZ')
        ts = time.time()
        utc_offset = datetime.datetime.fromtimestamp(ts) - datetime.datetime.utcfromtimestamp(ts)
        local = utc + utc_offset
        return local.timestamp()
    except Exception as e:
        print(e)
        return None


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('Pier One CLI {}'.format(pierone.__version__))
    ctx.exit()


def set_pierone_url(config: dict, url: str) -> None:
    '''Read Pier One URL from cli, from config file or from stdin.'''
    url = url or config.get('url')

    while not url:
        url = click.prompt('Please enter the Pier One URL', type=UrlType())

        try:
            requests.get(url, timeout=5)
        except:
            error('Could not reach {}'.format(url))
            url = None

    if '://' not in url:
        # issue 63: gracefully handle URLs without scheme
        url = 'https://{}'.format(url)

    config['url'] = url
    return url


@click.group(cls=AliasedGroup, context_settings=CONTEXT_SETTINGS)
@click.option('-V', '--version', is_flag=True, callback=print_version, expose_value=False, is_eager=True,
              help='Print the current version number and exit.')
@click.pass_context
def cli(ctx):
    ctx.obj = stups_cli.config.load_config('pierone')


@cli.command()
@url_option
@click.option('--realm', help='Use custom OAuth2 realm', metavar='NAME')
@click.option('-n', '--name', help='Custom token name (will be stored)', metavar='TOKEN_NAME', default='pierone')
@click.option('-U', '--user', help='Username to use for authentication', envvar='PIERONE_USER', metavar='NAME')
@click.option('-p', '--password', help='Password to use for authentication', envvar='PIERONE_PASSWORD', metavar='PWD')
@click.pass_obj
def login(config, url, realm, name, user, password):
    '''Login to Pier One Docker registry (generates ~/.dockercfg'''
    url_option_was_set = url
    url = set_pierone_url(config, url)
    user = user or os.getenv('USER')

    if not url_option_was_set:
        stups_cli.config.store_config(config, 'pierone')

    docker_login(url, realm, name, user, password, prompt=True)


def get_token():
    try:
        token = zign.api.get_token('pierone', ['uid'])
    except Exception as e:
        raise click.UsageError(str(e))
    return token


@cli.command()
@url_option
@output_option
@click.pass_obj
def teams(config, output, url):
    '''List all teams having artifacts in Pier One'''
    set_pierone_url(config, url)
    token = get_token()

    r = request(config.get('url'), '/teams', token)
    rows = [{'name': name} for name in sorted(r.json())]
    with OutputFormat(output):
        print_table(['name'], rows)


def get_artifacts(url, team: str, access_token):
    r = request(url, '/teams/{}/artifacts'.format(team), access_token)
    return r.json()


def get_tags(url, team, art, access_token):
    r = request(url, '/teams/{}/artifacts/{}/tags'.format(team, art), access_token)
    if r.status_code == 404:
        # empty list of tags (artifact does not exist)
        return []
    else:
        r.raise_for_status()
    return r.json()


@cli.command()
@click.argument('team', callback=validate_team)
@url_option
@output_option
@click.pass_obj
def artifacts(config, team, url, output):
    '''List all team artifacts'''
    set_pierone_url(config, url)
    token = get_token()

    result = get_artifacts(config.get('url'), team, token)
    rows = [{'team': team, 'artifact': name} for name in sorted(result)]
    with OutputFormat(output):
        print_table(['team', 'artifact'], rows)


@cli.command()
@click.argument('team', callback=validate_team)
@click.argument('artifact', nargs=-1)
@url_option
@output_option
@click.pass_obj
def tags(config, team: str, artifact, url, output):
    '''List all tags for a given team'''
    set_pierone_url(config, url)
    token = get_token()

    if not artifact:
        artifact = get_artifacts(config.get('url'), team, token)

    rows = []
    for art in artifact:
        r = get_tags(config.get('url'), team, art, token)
        rows.extend([{'team': team,
                      'artifact': art,
                      'tag': row['name'],
                      'created_by': row['created_by'],
                      'created_time': parse_time(row['created'])}
                     for row in r])

    # sorts are guaranteed to be stable, i.e. tags will be sorted by time (as returned from REST service)
    rows.sort(key=lambda row: (row['team'], row['artifact']))
    with OutputFormat(output):
        print_table(['team', 'artifact', 'tag', 'created_time', 'created_by'], rows,
                    titles={'created_time': 'Created', 'created_by': 'By'})


@cli.command()
@click.argument('team', callback=validate_team)
@click.argument('artifact')
@url_option
@output_option
@click.pass_obj
def latest(config, team, artifact, url, output):
    '''Get latest tag/version of a specific artifact'''
    # validate that the token exists!
    set_pierone_url(config, url)
    get_token()

    registry = config.get('url')
    if registry.startswith('https://'):
        registry = registry[8:]
    image = DockerImage(registry=registry, team=team, artifact=artifact, tag=None)

    print(get_latest_tag('pierone', image))


@cli.command('scm-source')
@click.argument('team', callback=validate_team)
@click.argument('artifact')
@click.argument('tag', nargs=-1)
@url_option
@output_option
@click.pass_obj
def scm_source(config, team, artifact, tag, url, output):
    '''Show SCM source information such as GIT revision'''
    set_pierone_url(config, url)
    token = get_token()

    tags = get_tags(config.get('url'), team, artifact, token)

    if not tag:
        tag = [t['name'] for t in tags]

    rows = []
    for t in tag:
        row = request(config.get('url'), '/teams/{}/artifacts/{}/tags/{}/scm-source'.format(team, artifact, t),
                      token).json()
        if not row:
            row = {}
        row['tag'] = t
        matching_tag = [d for d in tags if d['name'] == t]
        row['created_by'] = ''.join([d['created_by'] for d in matching_tag])
        if matching_tag:
            row['created_time'] = parse_time(''.join([d['created'] for d in matching_tag]))
        rows.append(row)

    rows.sort(key=lambda row: (row['tag'], row.get('created_time')))
    with OutputFormat(output):
        print_table(['tag', 'author', 'url', 'revision', 'status', 'created_time', 'created_by'], rows,
                    titles={'tag': 'Tag', 'created_by': 'By', 'created_time': 'Created',
                            'url': 'URL', 'revision': 'Revision', 'status': 'Status'},
                    max_column_widths={'revision': 10})


@cli.command('image')
@click.argument('image')
@url_option
@output_option
@click.pass_obj
def image(config, image, url, output):
    '''List tags that point to this image'''
    set_pierone_url(config, url)
    token = get_token()

    resp = request(config.get('url'), '/tags/{}'.format(image), token)

    if resp.status_code == 404:
        click.echo('Image {} not found'.format(image))
        return

    if resp.status_code == 412:
        click.echo('Prefix {} matches more than one image.'.format(image))
        return

    tags = resp.json()

    with OutputFormat(output):
        print_table(['team', 'artifact', 'name'],
                    tags,
                    titles={'name': 'Tag', 'artifact': 'Artifact', 'team': 'Team'})


@cli.command('inspect-contents')
@click.argument('team', callback=validate_team)
@click.argument('artifact')
@click.argument('tag', nargs=-1)
@click.option('-l', '--limit', type=int, default=1)
@url_option
@output_option
@click.pass_obj
def inspect_contents(config, team, artifact, tag, url, output, limit):
    '''List image contents (files in tar layers)'''
    set_pierone_url(config, url)
    token = get_token()

    tags = get_tags(config.get('url'), team, artifact, token)

    if not tag:
        tag = [t['name'] for t in tags]

    CHUNK_SIZE = 8192
    TYPES = {b'5': 'D', b'0': ' '}

    rows = []
    for t in tag:
        row = request(config.get('url'), '/v2/{}/{}/manifests/{}'.format(team, artifact, t),
                      token).json()
        if row.get('layers'):
            layers = reversed([lay.get('digest') for lay in row.get('layers')])
        else:
            layers = [lay.get('blobSum') for lay in row.get('fsLayers')]
        if layers:
            found = 0
            for i, layer in enumerate(layers):
                layer_id = layer
                if layer_id:
                    response = request(config.get('url'), '/v2/{}/{}/blobs/{}'.format(team, artifact, layer_id), token)
                    with tempfile.NamedTemporaryFile(prefix='tmp-layer-', suffix='.tar') as fd:
                        for chunk in response.iter_content(CHUNK_SIZE):
                            fd.write(chunk)
                        fd.flush()
                        with tarfile.open(fd.name) as archive:
                            has_member = False
                            for member in archive.getmembers():
                                rows.append({'layer_index': i, 'layer_id': layer_id, 'type': TYPES.get(member.type),
                                             'mode': oct(member.mode)[-4:],
                                             'name': member.name, 'size': member.size, 'created_time': member.mtime})
                                has_member = True
                            if has_member:
                                found += 1
                if found >= limit:
                    break

    rows.sort(key=lambda row: (row['layer_index'], row['name']))
    with OutputFormat(output):
        print_table(['layer_index', 'layer_id', 'mode', 'name', 'size', 'created_time'], rows,
                    titles={'created_time': 'Created', 'layer_index': 'Idx'},
                    max_column_widths={'layer_id': 16})


def main():
    cli()
