import click
from json import dumps, load
import os
import sys
from tabulate import tabulate

@click.group('request')
@click.pass_context
def cli(ctx):
    pass

@cli.command(name='unpause', help='Unpause a request')
@click.argument('request-id')
@click.pass_context
def request_unpause(ctx, request_id):
    res = ctx.obj['client'].unpause_request(request_id)
    if 'error' in res:
        click.echo('error during unpause request {0}: {1}'.format(request_id, res['error']))
    else:
        click.echo('unpaused request {0}'.format(request_id))

@cli.command(name='run', help='Run a on-demand request now')
@click.argument('request-id')
@click.pass_context
def request_run(ctx, request_id):
    res = ctx.obj['client'].run_request(request_id)
    if 'error' in res:
        click.echo('error during running request {0}: {1}'.format(request_id, res['error']))
    else:
        click.echo('running request {0}'.format(request_id))

@cli.command(name='pause', help='Pause a request')
@click.option('--kill-tasks', '-k', is_flag=True, default=False, help='Kill tasks when paused')
@click.argument('request-id')
@click.pass_context
def request_pause(ctx, request_id, kill_tasks):
    res = ctx.obj['client'].pause_request(request_id, kill_tasks)
    if 'error' in res:
        click.echo('error during pause request {0}: {1}'.format(request_id, res['error']))
    else:
        click.echo('paused request {0} with killTasks={1}'.format(request_id, kill_tasks))

@cli.command(name='scale', help='Scale a request up/down')
@click.argument('request-id')
@click.argument('instances', '-i', type=click.INT)
@click.pass_context
def request_scale(ctx, request_id, instances):
    res = ctx.obj['client'].scale_request(request_id, instances)
    if 'error' in res:
        click.echo('error during set instances for request {0}: {1}'.format(request_id, res['error']))
    else:
        click.echo('setting instances to {0} for request {1}'.format(instances, request_id))

@cli.command(name='bounce', help='Restart a request tasks')
@click.argument('request-id')
@click.pass_context
def request_bounce(ctx, request_id):
    res = ctx.obj['client'].bounce_request(request_id)
    if 'error' in res:
        click.echo('error during set instances for request {0}: {1}'.format(request_id, res['error']))
    else:
        click.echo('bounced request {0}'.format(request_id))

@cli.command(name='get', help='Get the state of a request')
@click.argument('request-id')
@click.option('--json', '-j', is_flag=True, help='Enable json output')
@click.pass_context
def request_get(ctx, request_id, json):
    if request_id:
        res = ctx.obj['client'].get_request(request_id)
        if json:
            click.echo(dumps(res, indent=2))
        else:
            output_request(res)

@cli.command(name='delete', help='Remove a request')
@click.argument('request-id')
@click.pass_context
def request_delete(ctx, request_id):
    res = ctx.obj['client'].delete_request(request_id)
    if 'error' in res:
        click.echo('error during delete request {0}: {1}'.format(request_id, res['error']))
    else:
        click.echo('deleted request {0}'.format(request_id))

@cli.command(name='list', help='Get a list of requests')
@click.option('--type', '-t', default='all', type=click.Choice(['pending', 'cleanup', 'paused', 'finished', 'cooldown', 'active', 'all']), help='Request type to get')
@click.option('--json', '-j', is_flag=True, help='Enable json output')
@click.pass_context
def request_list(ctx, type, json):
    res = ctx.obj['client'].get_requests(type)
    if json:
        click.echo(dumps(res, indent=2))
    else:
        output_requests(res)

@cli.command(name='sync', help='Sync one or more requests/deploys')
@click.option('--file', '-f', type=click.File('r'), help='JSON request/deploy file to sync')
@click.option('--dir',  '-d', type=click.Path(), help='Directory of JSON request/deploy files to sync')
@click.pass_context
def request_sync(ctx, file, dir):
    had_error = False
    client = ctx.obj['client']
    if file:
        file_request = None
        try:
            file_request = load(file)
        except ValueError as e:
            click.echo('json parse error: {0}'.format(e))
            had_error = True
        if file_request:
            sync_request(client, file_request)
    elif dir:
        for filename in os.listdir(dir):
            if filename.endswith('json'):
                with open(os.path.join(dir, filename)) as file:
                    file_request = None
                    try:
                        file_request = load(file)
                    except ValueError as e:
                        click.echo('json parse error: {0}'.format(e))
                        had_error = True
                    if file_request:
                        sync_request(client, file_request)
    else:
        click.echo('Either --file or --dir is required')
    if had_error:
        sys.exit(1)

def sync_request(client, request):
    requested_instances = request['request'].get('instances', 1)
    if requested_instances == 0:
        singularity_request = client.pause_request(request['request']['id'], kill_tasks=True)
        if 'error' in singularity_request:
            click.echo('error during sync request: {0}'.format(singularity_request['error']))
        else:
            click.echo('syncronized request {0}'.format(request['request']['id']))
    else:
        isPaused = False
        singularity_request = client.get_request(request['request']['id'])
        if 'error' in singularity_request and singularity_request['status_code'] == 404:
            pass # request didn't exist before
        else:
            if singularity_request and singularity_request['state'] == 'PAUSED' and requested_instances > 0:
                isPaused = True
                if not request.get('deploy', {}).get('pauseBeforeDeploy', False):
                    client.unpause_request(request['request']['id'])
                    isPaused = False
        singularity_request = client.upsert_request(request['request'])
        if 'error' in singularity_request:
            click.echo('error during sync request: {0}'.format(singularity_request['error']))
        else:
            click.echo('syncronized request {0}'.format(request['request']['id']))
        if 'deploy' in request:
            file_deploy_id = request['deploy'].get('id', None)
            # always set deploy.requestId to request.id from json file
            request['deploy']['requestId'] = request['request']['id']
            if 'activeDeploy' in singularity_request:
                singularity_deploy_id = singularity_request['activeDeploy'].get('id', None)
                if file_deploy_id != singularity_deploy_id:
                    sync_deploy(client, request['deploy'], isPaused)
            else:
                sync_deploy(client, request['deploy'], isPaused)

def sync_deploy(client, deploy, isPaused):
    unpauseOnSuccessfulDeploy = False
    if deploy.get('pauseBeforeDeploy', False):
        del deploy['pauseBeforeDeploy']
        unpauseOnSuccessfulDeploy = True
        if not isPaused:
            pause_deploy_and_wait(client, deploy)

    res = client.create_deploy(deploy, unpauseOnSuccessfulDeploy)
    if 'error' in res:
        click.echo('error during sync deploy: {0}'.format(res['error']))
    else:
        click.echo('syncronized deploy {0} for request {1}'.format(deploy['id'], deploy['requestId']))

    return res

def pause_deploy_and_wait(client, deploy):
    singularity_request = client.pause_request(deploy['requestId'], kill_tasks=True)
    if 'error' in singularity_request:
        click.echo('error during pause request: {0}'.format(singularity_request['error']))
    else:
        click.echo('pausing request {0} before deploy'.format(deploy['requestId']))
    if singularity_request:
        active_deploy_id = singularity_request.get('activeDeploy', {}).get('id', None)
        if active_deploy_id:
            no_tasks = False
            while not no_tasks:
                tasks = client.get_active_deploy_tasks(deploy['requestId'], active_deploy_id)
                if len(tasks) == 0:
                    no_tasks = True
        click.echo('killed all tasks for request {0}'.format(deploy['requestId']))


@cli.command(name='clean', help='Remove requests not in the specified directory')
@click.argument('dir', type=click.Path())
@click.pass_context
def request_clean(ctx, dir):
    client = ctx.obj['client']
    requests = client.get_requests('all')
    for request in requests:
        request_id = request['request']['id']
        if not os.path.isfile(os.path.join(dir, '{0}.json'.format(request_id))):
            res = client.delete_request(request_id)
            if 'error' in res:
                click.echo('error during delete request {0}: {1}'.format(request_id, res['error']))
            else:
                click.echo('deleted request {0}'.format(request_id))

def output_request(request):
    request_output = [
        ['Id', request.get('request', {}).get('id', 'unknown')],
        ['State', request.get('state')],
        ['Type', request.get('request', {}).get('requestType', 'unknown')],
        ['Instances', request.get('request', {}).get('instances', 1)],
        ['Rack Sensitive', request.get('request', {}).get('rackSensitive', 'unknown')],
        ['Load Balanced', request.get('request', {}).get('loadBalanced', 'unknown')],
        ['Owners', request.get('request', {}).get('owners', 'unknown')],
        ['Deploy Id', request.get('activeDeploy', {}).get('id', 'unknown')],
    ]
    click.echo(tabulate(request_output))

def output_requests(requests):
    requests_output = [['Id', 'State', 'Type', 'Instances', 'Deploy Id']]
    for request in requests:
        requests_output.append([
            request.get('request', {}).get('id', 'unknown'),
            request.get('state', 'unknown'),
            request.get('request', {}).get('requestType', 'unknown'),
            request.get('request', {}).get('instances', 1),
            request.get('requestDeployState', {}).get('activeDeploy', {}).get('deployId', 'none')
        ])
    click.echo(tabulate(requests_output, headers="firstrow"))
