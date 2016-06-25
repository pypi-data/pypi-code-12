# -*- coding:utf-8 -*-

import click


@click.command()
@click.option('--count', default=1, help='number of greetings.')
@click.option('--name', prompt='Your name', help='The person to greet.')
def hello(count, name):
    """
    teste
    :param count:
    :param name:
    :return:
    """
    for x in range(count):
        click.echo('Hello {}!'.format(name))


if __name__ == '__main__':
    hello()


