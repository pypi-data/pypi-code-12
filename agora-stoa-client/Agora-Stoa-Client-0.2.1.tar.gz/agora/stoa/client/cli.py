import json

import click
import re
from rdflib import Graph

from agora.stoa.client import get_fragment_generator,get_query_generator


@click.group()
def cli():
    pass


@click.command()
@click.argument('gp', type=click.STRING)
@click.option('--broker', '-b', default=('localhost', 5672), type=(click.STRING, click.INT))
@click.option('--agora', '-a', default=('localhost', 9002), type=(click.STRING, click.INT))
@click.option('--channel', '-c', default=('stoa', 'stoa.request', 'stoa.response'),
              type=(click.STRING, click.STRING, click.STRING))
@click.option('--updating', '-u', default=10, type=click.INT)
@click.option('--gen', '-g', default=False, type=click.BOOL)
def fragment(gp, broker, agora, channel, updating, gen):
    try:
        gp_match = re.search(r'\{(.*)\}', gp).groups(0)
        if len(gp_match) != 1:
            raise click.ClickException('Invalid graph pattern')

        STOA = {
            "broker_host": broker[0],
            "broker_port": broker[1],
            "agora_host": agora[0],
            "agora_port": agora[1],
            "exchange": channel[0],
            "topic_pattern": channel[1],
            "response_prefix": channel[2]
        }

        tps = re.split('\. ', gp_match[0])

        prefixes, fragment_gen = get_fragment_generator(*tps, monitoring=30, STOA=STOA, updating=updating, gen=gen)
        graph = Graph()
        for prefix in prefixes:
            graph.bind(prefix, prefixes[prefix])
            click.echo('@prefix {}: <{}> .'.format(prefix, prefixes[prefix]))
        click.echo('')

        for chunk in fragment_gen:
            if chunk is not None:
                headers, (c, s, p, o) = chunk
                triple = u'{} {} {} .'.format(s.n3(graph.namespace_manager), p.n3(graph.namespace_manager),
                                              o.n3(graph.namespace_manager))
                click.echo(triple)
    except Exception as e:
        raise click.ClickException('There was a problem with the request: {}'.format(e.message))


@click.command()
@click.argument('gp', type=click.STRING)
@click.option('--broker', '-b', default=('localhost', 5672), type=(click.STRING, click.INT))
@click.option('--agora', '-a', default=('localhost', 9002), type=(click.STRING, click.INT))
@click.option('--channel', '-c', default=('stoa', 'stoa.request', 'stoa.response'),
              type=(click.STRING, click.STRING, click.STRING))
@click.option('--updating', '-u', default=10, type=click.INT)
@click.option('--gen', '-g', default=False, type=click.BOOL)
def query(gp, broker, agora, channel, updating, gen):
    try:
        gp_match = re.search(r'\{(.*)\}', gp).groups(0)
        if len(gp_match) != 1:
            raise click.ClickException('Invalid graph pattern')

        STOA = {
            "broker_host": broker[0],
            "broker_port": broker[1],
            "agora_host": agora[0],
            "agora_port": agora[1],
            "exchange": channel[0],
            "topic_pattern": channel[1],
            "response_prefix": channel[2]
        }

        tps = re.split('\. ', gp_match[0])

        _, query_gen = get_query_generator(*tps, monitoring=30, STOA=STOA, updating=updating, gen=gen)
        click.secho('[', nl=False, bold=True)
        first_row = True
        for chunk in query_gen:
            if chunk is not None:
                _, row = chunk
                row_json = json.dumps(row)
                row_str = ',\n  {}'.format(row_json)
                if first_row:
                    row_str = row_str.lstrip(',')
                first_row = False
                click.secho(row_str, nl=False)
        click.secho('\n]', bold=True)
    except Exception as e:
        raise click.ClickException('There was a problem with the request: {}'.format(e.message))


cli.add_command(query)
cli.add_command(fragment)

if __name__ == '__main__':
    cli()
