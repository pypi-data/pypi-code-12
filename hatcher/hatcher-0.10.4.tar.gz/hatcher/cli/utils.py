#
# Canopy product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#
from __future__ import absolute_import, print_function

from datetime import datetime
from functools import wraps
import sys

from requests.exceptions import HTTPError, SSLError
import click
from click.utils import make_str
from click.core import iter_params_for_processing
import pytz
import tzlocal

from okonomiyaki.versions import PEP440Version

from hatcher.api import BroodClient
from hatcher.errors import HatcherException
from hatcher.core.model_registry import MAX_API_VERSION


_click_version = PEP440Version.from_string(click.__version__)

IS_CLICK_6 = _click_version >= PEP440Version.from_string('6.0')

if IS_CLICK_6:
    from click.core import _check_multicommand


class BroodClientProxy(object):
    """A proxy object to the ``BroodClient`` that handles lazy verification
    of the brood ``url``.  When a subcommand is executed, this proxy
    will automatically verify that the required ``url`` is set; if not,
    will exit with an error using the standard ``click`` interfaces.

    """

    def __init__(self, url, auth, api_version, url_param, ctx, verify_ssl=True,
                 debug=False):
        self.url = url
        self.auth = auth
        self.api_version = api_version
        self.url_param = url_param
        self.ctx = ctx
        self.brood_client = None
        self.verify_ssl = verify_ssl
        self.debug = debug

    def __getattr__(self, name):
        if self.url is None:
            raise click.MissingParameter(ctx=self.ctx, param=self.url_param)
        if self.brood_client is None:
            self.brood_client = BroodClient.from_url(
                self.url, auth=self.auth, verify_ssl=self.verify_ssl,
                api_version=self.api_version)
        return getattr(self.brood_client, name)


class _ErrorHandlingMixin(object):

    def invoke(self, ctx):
        try:
            return super(_ErrorHandlingMixin, self).invoke(ctx)
        except HatcherException as exc:
            if ctx.obj.debug:
                raise
            click.echo(click.style(str(exc), fg='red'), err=True)
            sys.exit(-1)
        except HTTPError as exc:
            if ctx.obj.debug:
                raise
            response = exc.response
            content_type = response.headers.get('Content-Type', '')
            if content_type == 'application/json':
                error = response.json()
                if 'error' in error:
                    click.echo(click.style(error['error'], fg='red'), err=True)
                    sys.exit(-1)
            raise
        except SSLError as exc:
            if ctx.obj.debug:
                raise
            error = 'SSL error: {0}'.format(str(exc))
            url = ctx.obj.url
            click.echo(click.style(str(exc), fg='red'), err=True)
            click.echo(
                'To connect to {0} insecurely, pass the `--insecure` flag to '
                'hatcher.'.format(url), err=True)
            sys.exit(-1)
        except (click.ClickException, click.Abort):
            # We don't want to intercept internal click exceptions here.
            raise
        except Exception as exc:
            if ctx.obj.debug:
                raise
            click.echo(click.style('Unexpected error', fg='red'), err=True)
            click.echo(click.style(repr(exc), fg='red'), err=True)
            sys.exit(-1)


class HatcherClickGroup(_ErrorHandlingMixin, click.Group):

    def _Command_parse_args(self, ctx, args):
        parser = self.make_parser(ctx)
        opts, args, param_order = parser.parse_args(args=args)

        param_names = [p.name for p in param_order]
        try:
            idx = param_names.index('api_version')
        except ValueError:
            pass
        else:
            param_order = (
                [param_order[idx]] + param_order[:idx] + param_order[idx + 1:])

        for param in iter_params_for_processing(
                param_order, self.get_params(ctx)):
            value, args = param.handle_parse_result(ctx, opts, args)

        if args and not ctx.allow_extra_args and not ctx.resilient_parsing:
            ctx.fail('Got unexpected extra argument%s (%s)'
                     % (len(args) != 1 and 's' or '',
                        ' '.join(map(make_str, args))))

        ctx.args = args
        return args

    def parse_args(self, ctx, args):
        if not args and self.no_args_is_help and not ctx.resilient_parsing:
            click.echo(ctx.get_help(), color=ctx.color)
            ctx.exit()
        rest = self._Command_parse_args(ctx, args)

        if IS_CLICK_6:
            if self.chain:
                ctx.protected_args = rest
                ctx.args = []
            elif rest:
                ctx.protected_args, ctx.args = rest[:1], rest[1:]
            return ctx.args
        else:
            return rest

    @staticmethod
    def _api_version_from_ctx(ctx):
        ctx = ctx.find_root()
        if ctx.obj is None:
            return int(ctx.params.get('api_version', MAX_API_VERSION))
        else:
            return ctx.obj.api_version

    def add_command(self, cmd, api_version, name=None):
        """Registers another :class:`Command` with this group.  If the name
        is not provided, the name of the command is used.
        """
        name = name or cmd.name
        if name is None:
            raise TypeError('Command has no name.')
        if IS_CLICK_6:
            _check_multicommand(self, name, cmd, register=True)
        self.commands.setdefault(api_version, {})[name] = cmd

    def command(self, *args, **kwargs):
        """A shortcut decorator for declaring and attaching a command to
        the group.  This takes the same arguments as :func:`command` but
        immediately registers the created command with this instance by
        calling into :meth:`add_command`.
        """
        def decorator(f):
            api_versions = kwargs.pop('api_versions', [])
            if len(api_versions) == 0:
                # fixme
                api_versions = [kwargs.pop('api_version')]
            cmd = click.command(*args, **kwargs)(f)
            for api_version in api_versions:
                self.add_command(cmd, api_version)
            return cmd
        return decorator

    def group(self, *args, **kwargs):
        """A shortcut decorator for declaring and attaching a group to
        the group.  This takes the same arguments as :func:`group` but
        immediately registers the created command with this instance by
        calling into :meth:`add_command`.
        """
        def decorator(f):
            api_versions = kwargs.pop('api_versions', [])
            if len(api_versions) == 0:
                # fixme
                api_versions = [kwargs.pop('api_version', 0)]
            kwargs.setdefault('cls', HatcherClickGroup)
            cmd = click.group(*args, **kwargs)(f)
            for api_version in api_versions:
                self.add_command(cmd, api_version)
            return cmd
        return decorator

    def get_command(self, ctx, cmd_name):
        api_version = self._api_version_from_ctx(ctx)
        return self.commands.get(api_version, {}).get(cmd_name)

    def list_commands(self, ctx):
        api_version = self._api_version_from_ctx(ctx)
        return sorted(self.commands.get(api_version, []))


class HTTPErrorHandlingUploadCommand(_ErrorHandlingMixin, click.Command):

    def invoke(self, ctx):
        try:
            return super(HTTPErrorHandlingUploadCommand, self).invoke(ctx)
        except HTTPError as exc:
            if ctx.obj.debug:
                raise
            status_code = exc.response.status_code
            if status_code == 401:
                click.echo(click.style('Authentication failed', fg='red'),
                           err=True)
                sys.exit(-1)
            elif status_code == 404:
                params = ctx.params
                organization_name = params.get('organization')
                repository_name = params.get('repository')
                if repository_name is None or organization_name is None:
                    error = 'Not found'
                else:
                    repo_name = '{0}/{1}'.format(
                        organization_name, repository_name)
                    error = 'No such repository: {0!r}'.format(repo_name)
                click.echo(click.style(error, fg='red'), err=True)
                sys.exit(-1)
            raise


pass_brood_client = click.make_pass_decorator(BroodClientProxy)


def add_arguments(fn, *arguments):
    """Add click arguments to a function.  The arguments will appear in the
    CLI in the same order as they are passed to this function.

    """
    for argname in reversed(arguments):
        fn = click.argument(argname)(fn)
    return fn


def pass_organization(fn):
    @wraps(fn)
    def wrapper(brood_client, organization, *args, **kwargs):
        org = brood_client.organization(organization)
        return fn(organization=org, *args, **kwargs)
    return pass_brood_client(wrapper)


def pass_repository(fn):
    @wraps(fn)
    def wrapper(brood_client, organization, repository, *args, **kwargs):
        repo = brood_client.organization(organization).repository(repository)
        return fn(repository=repo, *args, **kwargs)
    return pass_brood_client(wrapper)


def pass_team(fn):
    @wraps(fn)
    def wrapper(brood_client, organization, team, *args, **kwargs):
        org = brood_client.organization(organization)
        team = org.team(team)
        return fn(team=team, *args, **kwargs)
    return pass_brood_client(wrapper)


def get_localtime():
    utcnow = datetime.now(tz=pytz.utc)
    try:
        localzone = tzlocal.get_localzone()
    except pytz.UnknownTimeZoneError:
        return utcnow
    else:
        return utcnow.astimezone(localzone)


def get_timeformat():
    return '%Y-%m-%d %H:%M:%S %Z (%z)'


def upload_context_table(ctx, name, filename, repository, platform=None):
    format_ = get_timeformat()
    localtime = get_localtime()
    rows = [
        ['{0} upload'.format(name), filename],
        ['Server', ctx.obj.url],
        ['Repository', str(repository)],
    ]
    if platform is not None:
        rows.append(['Platform', platform])
    rows.append(['Time', localtime.strftime(format_)])
    return rows
