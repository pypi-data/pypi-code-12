import os
import click
from maintain.config import Config
from maintain.creators import load_creators, ValidationError


@click.group()
def cli():
    pass


@click.command()
@click.argument('name')
@click.argument('configs', nargs=-1)
@click.option('--dry-run', is_flag=True, default=False)
def create(name, configs, dry_run):
    config = Config.gather(configs)
    creators = load_creators(config, name)

    for creator in creators:
        try:
            creator.validate()
        except ValidationError as e:
            click.echo('{}: {}'.format(creator.name, e), err=True)
            exit(1)

    if dry_run:
        for creator in creators:
            click.echo(creator)
        exit(0)

    with click.progressbar(length=len(creators) * 3, label='Creating project') as progress:
        count = 0

        for creator in creators:
            creator.pre_create()
            progress.update(count)
            count += 1

        for creator in creators:
            creator.create()
            progress.update(count)
            count += 1

        for creator in creators:
            creator.post_create()
            progress.update(count)
            count += 1

cli.add_command(create)

