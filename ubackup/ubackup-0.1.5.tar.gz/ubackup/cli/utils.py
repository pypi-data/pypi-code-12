import click
import sys
import requests
from dateutil import tz
from ubackup import settings
from ubackup.utils import filesizeformat


def ask_for_rev(revisions):
    rev_to_restore = revisions[0]

    if len(revisions) > 1:
        to_zone = tz.tzlocal()
        for i, rev in enumerate(revisions):
            sys.stdout.write('%(i)2s. %(date)s: %(size)s\n' % {
                'i': i,
                'date': rev['date'].astimezone(to_zone).strftime('%Y-%m-%d %H:%M:%S'),
                'size': filesizeformat(rev['size'])
            })
        sys.stdout.flush()
        response = click.prompt(
            "Which version do you want to restore?",
            type=click.IntRange(min=0, max=len(revisions) - 1),
            prompt_suffix=' ')
        rev_to_restore = revisions[response]

    return rev_to_restore


def dropbox_token_flow():
    click.echo(click.style('The application will load an URL into your browser.', fg='blue'))
    click.echo(click.style('You have to authorize the application to access to your account.', fg='blue'))
    click.echo(click.style('When the access is granted, dropbox will return you a key.', fg='blue'))
    click.pause()
    click.launch(
        'https://www.dropbox.com/1/oauth2/authorize?client_id=%s&response_type=code' % settings.DROPBOX_APP_KEY)
    key = click.prompt(click.style('Please enter the dropbox returned key', bold=True))
    click.echo(click.style('Processing...', fg='blue'))

    query = requests.post(
        url='https://api.dropbox.com/1/oauth2/token',
        params={
            'grant_type': 'authorization_code',
            'code': key,
            'client_id': settings.DROPBOX_APP_KEY,
            'client_secret': settings.DROPBOX_APP_SECRET,
        })
    data = query.json()
    if 'error' in data:
        click.echo(click.style('Dropbox returned an error: %s' % data['error_description'], fg='red'))
    elif 'access_token' not in data:
        click.echo(click.style('An unknow error has occured, please retry later.', fg='red'))
    else:
        click.echo(click.style('Here is your token: %s' % click.style(data['access_token'], fg='green'), fg='blue'))
        click.echo(click.style('Please save it in your uBackup settings.', fg='blue'))
