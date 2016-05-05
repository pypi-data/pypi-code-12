import click
import client
import settings


@click.command()
@click.argument('twitter')
@click.option('--hours', default=24)
@click.option('--data', default=settings.data_path)
@click.option('--output', default=settings.content_path)
@click.option('--email', default=None)
@click.option('--name', default=None)
@click.option('--test', default=False)
def run(twitter, hours, data, output, email, name, test):
    if not test:
        client.ticktock(twitter, hours, data, output, email, name)
    else:
        click.echo('Conversationalist test.')


# Call run function when module deployed as script. This is approach is common
# within the python community
if __name__ == '__main__':
    #client.ticktock2()
    run()

