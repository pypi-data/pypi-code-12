import click
import mezzanine_client
import json
import requests.exceptions
import os
import datetime
import markdown2
import pprint

from .config import Parser, settings
from .errors import MezzanineCLIError


# Mezzanine content status constants
CONTENT_STATUS_DRAFT = 1
CONTENT_STATUS_PUBLISHED = 2


def get_client():
    """
    Return an API client for making requests.
    """
    if not settings.client_id or not settings.client_secret:
        raise MezzanineCLIError('Please configure the CLI. See "mezzanine-cli config --help".'
                                'Or visit http://gcushen.github.io/mezzanine-api/cli/ for more information.')
    return mezzanine_client.Mezzanine(credentials=(settings.client_id, settings.client_secret),
                                      api_url=settings.api_url)


@click.group(invoke_without_command=True,
             help='Command line client for interacting with Mezzanine API services.\n\n'
                  'Visit http://gcushen.github.io/mezzanine-api/cli/ for more information.')
@click.option('--version', is_flag=True, help='Display the Mezzanine API CLI version.')
@click.pass_context
def client(ctx, version):
    if ctx.invoked_subcommand is not None:
        return

    if version:
        click.echo('mezzanine-client version {}'.format(mezzanine_client.__version__))
    else:
        click.echo(ctx.get_help())


@click.command(help='Clears the credentials and resets CLI configuration.')
def logout():
    filename = os.path.expanduser('~/.mezzanine.cfg')
    if os.path.exists(filename):
        os.remove(filename)

    click.echo('You have been logged out.')


@click.group(help="Create or show blog posts.")
def posts():
    pass


@click.command(help="List posts.")
@click.option('--offset', default=0, help='Result offset.')
@click.option('--limit', default=10, help='Result limit.')
def posts_list(offset, limit):
    api = get_client()
    published_posts = api.get_posts(offset=offset, limit=limit)

    click.echo(click.style('Published Posts', bold=True))
    fmt = '{id} <{title} {url}>'
    for post in published_posts:
        print(fmt.format(id=post['id'], title=post['title'], url=post['url']))


@click.command(help="Fetch the post with the given ID.")
@click.argument('id', nargs=1)
def posts_get(id):
    api = get_client()

    try:
        post = api.get_post(int(id))
    except (requests.exceptions.HTTPError, ValueError):
        click.echo(click.style(u'Post "{0}" does not exist.'.format(id), fg='red'))
        return

    click.echo(json.dumps(post, indent=4, ensure_ascii=False))


@click.command(help="Create new post.")
@click.option('--title', default='', help='Post title.')
@click.option('--content', default='', help='Post content.')
@click.option('--content-file', default=None, help='Specify a file to load post content from.')
@click.option('--publish_date', default='', help='ISO datetime stamp to publish post at (e.g. '
                                                 '"YYYY-MM-DDTHH:MM:SS" where "T" is separator). '
                                                 'If unset, defaults to now.')
@click.option('--categories', default='', help='Comma delimited category list. Auto-creates new categories.')
@click.option('--markdown', is_flag=True, help='Read Markdown formatted content.')
@click.option('--draft', is_flag=True, help='Save as draft, do not publish.')
@click.option('--dry-run', is_flag=True, help='Displays the data to be saved without actually sending it to API.')
def posts_create(title, content, content_file, categories, publish_date, markdown, dry_run, draft):
    api = get_client()

    # Get contents from file if file is specified.
    if content_file:
        try:
            file = open(os.path.expanduser(content_file), 'r')
            content = file.read()
        except (IOError, OSError) as e:
            raise MezzanineCLIError('Could not read file specified in `--content-file` parameter! "{}".'.format(e))

        if not title or not content:
            raise MezzanineCLIError('Please specify `--title` and `--content` options!')

    # Strip any whitespace from beginning and end of string.
    content = content.strip()

    # Convert any Markdown to HTML.
    if markdown:
        content = markdown2.markdown(content)

    # Escape the HTML content ready for JSON whilst removing \n and the added quotes that enclose the string.
    content_processed = json.dumps(content).replace('\\n', '')[1:-1]

    if not publish_date:
        publish_date = datetime.datetime.utcnow().isoformat()

    if draft:
        status = CONTENT_STATUS_DRAFT
    else:
        status = CONTENT_STATUS_PUBLISHED

    blog_post_data = {'title': title.strip(),
                      'content': content_processed,
                      'categories': categories.strip(),
                      'publish_date': publish_date.strip(),
                      'status': status
                      }

    # Simulate the API write operation with a dry-run if desired.
    if dry_run:
        click.echo(click.style('Performing dry run...', fg='blue', bold=True))
        pprint.pprint(blog_post_data)
        return

    # Publish new blog article via POST to API.
    try:
        response = api.create_post(blog_post_data)
    except requests.exceptions.HTTPError as e:
        raise MezzanineCLIError('Check `--title` and `--content` options were correctly provided!'
                                'Add `--help` to your command for available options.'
                                '\nDetails: "{}".'.format(e))

    # If request was successful, print confirmation.
    if 'id' in response:
        # Note: this will display the URL of the post in the browsable API, since we cannot get the generated slug URL
        # for the formatted post without sending a read request.
        post_url = settings.api_url + '/posts/' + str(response['id'])
        click.echo(click.style('Blog post successfully published with ID #{} <{} {}>'.format(
            response['id'], title.strip(), post_url), fg='green', bold=True))


@click.command(help="Read or write CLI configuration.")
@click.argument('key', required=False)
@click.argument('value', required=False)
def config(key=None, value=None):
    """
    Read or write Mezzanine Client configuration.
    """

    # User settings file.
    filename = os.path.expanduser('~/.mezzanine.cfg')

    # If not setting a parameter, display current configuration.
    if not key:
        # Brief description of each available parser.
        parser_desc = {
            'user': 'User options (stored in ~/.mezzanine.cfg).',
            'defaults': 'Default options.',
        }

        # Iterate over each config parser from highest to lowest precedence.
        # Hence user settings override default settings.
        seen = set()
        for name, parser in zip(settings.parsers_available, settings.get_parsers):
            # Check if there are any settings in this parser which are in effect and not overridden.
            found = False
            for option in parser.options('general'):
                if option in seen:
                    continue
                found = True

            # Print header.
            if found:
                click.secho('# {}'.format(parser_desc[name]), fg='green', bold=True)

            # Iterate over each option in the parser and print the first instance of each option found.
            for option in parser.options('general'):
                if option in seen:
                    continue
                show_setting(option)
                seen.add(option)

            # Format output.
            if found:
                click.echo('')
        return

    # Abort if invalid option found.
    if not hasattr(settings, key):
        raise MezzanineCLIError('Invalid configuration option "{}".'.format(key))

    # If only a key is provided, print its value.
    if key and not value:
        show_setting(key)
        return

    # If this stage is reached, we are saving a value to the config file.
    parser = Parser()
    parser.add_section('general')
    parser.read(filename)
    parser.set('general', key, value)
    with open(filename, 'w') as file:
        parser.write(file)
    click.echo(click.secho('Configuration updated successfully.', fg='green'))


def show_setting(key):
    """
    Display a setting in the CLI.
    """
    value = getattr(settings, key)
    click.secho('{}: '.format(key), fg='magenta', bold=True, nl=False)
    click.secho(str(value), bold=True, fg='white' if isinstance(value, str) else 'cyan')


# Register commands.

client.add_command(config)
client.add_command(logout)

client.add_command(posts)
posts.add_command(posts_create, name='create')
posts.add_command(posts_get, name='get')
posts.add_command(posts_list, name='list')


if __name__ == '__main__':
    client()
