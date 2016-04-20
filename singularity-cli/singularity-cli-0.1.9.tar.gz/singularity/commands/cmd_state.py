import click
from json import dumps
from tabulate import tabulate

# singularity state api
@click.command('state')
@click.option('--underprovisioned', '-u', is_flag=True, help='Show list of underprovisioned requests')
@click.option('--overprovisioned',  '-o', is_flag=True, help='Show list of overprovisioned requests')
@click.option('--json', '-j', is_flag=True, help='Enable json output')
@click.pass_context
def cli(ctx, underprovisioned, overprovisioned, json):
    if underprovisioned:
        res = ctx.obj['client'].get_state_underprovisioned()
        #TODO: provide non json output
        click.echo(dumps(res, indent=2))
    elif overprovisioned:
        res = ctx.obj['client'].get_state_overprovisioned()
        #TODO: provide non json output
        click.echo(dumps(res, indent=2))
    else:
        res = ctx.obj['client'].get_state()
    	if json:
    		click.echo(dumps(res, indent=2))
    	else:
    		output_singularity_state(res)

def output_singularity_state(state):
	requests = [
		['Active', 'Paused', 'Cooling Down', 'Pending', 'Cleaning'],
		[state['activeRequests'], state['pausedRequests'], state['cooldownRequests'],
		state['pendingRequests'], state['cleaningRequests']]
	]
	click.echo('Requests\n')
	click.echo(tabulate(requests, headers="firstrow"))

	tasks = [
		['Active', 'Scheduled', 'Overdue', 'Cleaning', 'Load Balancer Cleanup'],
		[state['activeTasks'], state['scheduledTasks'], state['lateTasks'], state['cleaningTasks'], state['lbCleanupTasks']]
	]
	click.echo('Tasks\n')
	click.echo(tabulate(tasks, headers="firstrow"))

	racks = [
		['Active', 'Decommissioning', 'Inactive'],
		[state['activeRacks'], state['decommissioningRacks'], state['deadRacks'] ]
	]
	click.echo('Racks\n')
	click.echo(tabulate(racks, headers="firstrow"))

	slaves = [
		['Active', 'Decommissioning', 'Inactive', 'Unknown'],
		[state['activeSlaves'], state['decommissioningSlaves'], state['deadSlaves'], state['unknownSlaves']]
	]
	click.echo('Slaves\n')
	click.echo(tabulate(slaves, headers="firstrow"))
