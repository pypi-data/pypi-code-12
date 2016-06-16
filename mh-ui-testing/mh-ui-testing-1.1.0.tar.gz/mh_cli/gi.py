import click
from mh_cli import cli
from mh_cli.common import pass_state, state_callback

from fabric.api import local, settings, hide
from multiprocessing import cpu_count


def test_option(f):
    return click.option('--test',
                        expose_value=False,
                        help='ID of a ghost inspector test',
                        multiple=True,
                        callback=state_callback)(f)


def suite_option(f):
    return click.option('--suite',
                        expose_value=False,
                        help='ID of a ghost inspector suite',
                        multiple=True,
                        callback=state_callback)(f)


def key_option(f):
    return click.option('--key',
                        expose_value=False,
                        help='ghost inspector API key',
                        envvar='GI_API_KEY',
                        callback=state_callback)(f)


def var_option(f):
    return click.option('--var',
                        expose_value=False,
                        help='extra test variable(s); repeatable',
                        multiple=True,
                        callback=state_callback)(f)


def runners_option(f):
    return click.option('--runners',
                        expose_value=False,
                        help='num tests to run concurrently [default: %d]'
                             % (cpu_count() / 2),
                        default=cpu_count() / 2,
                        callback=state_callback)(f)


def gi_list_options(f):
    f = test_option(f)
    f = suite_option(f)
    f = key_option(f)
    return f


def gi_exec_options(f):
    f = gi_list_options(f)
    f = var_option(f)
    f = runners_option(f)
    return f


@cli.group()
def gi():
    """Do stuff with Ghost Inspector tests"""


@gi.command(name='list')
@gi_list_options
@pass_state
def gi_list(state):
    """Collect and list available tests"""
    params = ['--gi_key %s' % state.key]
    if state.test:
        params.extend('--gi_test %s' % x for x in state.test)
    if state.suite:
        params.extend('--gi_suite %s' % x for x in state.suite)
    _pytest_cmd('py.test --collect-only ' + ' '.join(params))


@gi.command(name='exec')
@gi_exec_options
@pass_state
def gi_exec(state):
    """Execute tests"""
    params = [
        '--gi_key %s' % state.key,
        '-n %d' % state.runners
    ]
    if state.test:
        params.extend('--gi_test %s' % x for x in state.test)
    if state.suite:
        params.extend('--gi_suite %s' % x for x in state.suite)
    if state.var:
        params.extend('--gi_param %s' % x for x in state.var)
    _pytest_cmd('py.test ' + ' '.join(params))


def _pytest_cmd(cmd):
    with settings(
            hide('warnings'),
            hide('running'),
            warn_only=True):
        local(cmd)
