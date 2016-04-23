from getpass import getpass
import os
import sys
import clip
import pika
from colorama import init, Back, Fore, Style
from configobj import ConfigObj

app = clip.App()

CONFIG_FILE_PATH = os.path.expanduser("~/.amqpclirc")
if os.path.exists(CONFIG_FILE_PATH):
    USER_MAP = ConfigObj(infile=CONFIG_FILE_PATH,
                         encoding='utf8')
else:
    USER_MAP = ConfigObj(encoding='utf8')
    USER_MAP.filename = CONFIG_FILE_PATH


def get_password(user):
    password = os.getenv('AMQP_PASSWORD', None)
    if password:
        return password
    user_record = USER_MAP['users'].get(user, None)
    if user_record:
        return user_record['password']
    return getpass(Fore.GREEN + "Password: " + Fore.RESET)


def get_vhost(user):
    vhost = os.getenv('AMQP_VHOST', None)
    if vhost:
        return vhost
    user_record = USER_MAP['users'].get(user, None)
    if user_record:
        return user_record['vhost']
    return '/'


def colorize(nocolor):
    init(strip=nocolor)


def print_failure(message, out=sys.stderr):
    out.write("%s%s%s\n" % (Fore.RED, message, Fore.RESET))


def print_success(message):
    sys.stdout.write("%s%s%s\n" % (Fore.GREEN, message, Fore.RESET))


@app.main(description='A command line interface for interacting with '
                      'amqp exchanges')
@clip.flag('-n', '--nocolor', name='nocolor',
           default=False, hidden=True,
           help='Do not colorize output',
           inherit_only=True, callback=colorize)
def amqpcli():
    pass


@amqpcli.subcommand(name='send',
                    description='Send a message to an exchange',
                    inherits=('nocolor',)
                    )
@clip.arg('host', name='host', required=True,
          help='Address of the amqp server')
@clip.arg('port', name='port', type=int, required=True,
          help='Port of the amqp server')
@clip.arg('exchange', name='exchange', required=True,
          help='Name of the exchange being sent to')
@clip.arg('routing_key', name='routing_key', required=True,
          help='The routing key for the message')
@clip.opt('-m', '--message', name='message', required=False,
          help='String to use as the message body')
@clip.opt("-f", "--file-path", name="file_path", required=False,
          help="Path of a file to use as the message body",
          default=None)
@clip.flag('-p', '--persistent', name='persistent',
           help='Make the message persistent if routed to a durable queue',
           default=False)
@clip.flag('-s', '--ssl', name='ssl',
           help='Use ssl/tls as the connection protocol',
           default=False)
@clip.opt('-u', '--user', name='user',
          help='User to connect to the queue as')
@clip.opt('-v', '--vhost', name='vhost',
          help='The vhost to connect to',
          required=False, default=None)
def amqp_send(host, port, exchange, routing_key, message,
              file_path, user, persistent, vhost, ssl, **kwargs):
    if not user:
        user = os.getenv('AMQP_USER', None)
    if not user:
        user = input(Fore.GREEN + "User: " + Fore.RESET)
    password = get_password(user)
    vhost = vhost or get_vhost(user)

    if not ((message is None) ^ (file_path is None)):
        print_failure('Exactly one option (-f) or (-m) '
                      'must be specified',)
        clip.exit(err=True)

    properties = pika.BasicProperties(delivery_mode=2 if persistent else 1)
    credentials = pika.PlainCredentials(user, password)
    print("Connecting to queue @ %s:%s... " % (host, port), end="")
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(
                                             host=host, port=port, ssl=ssl,
                                             virtual_host=vhost,
                                             credentials=credentials))
    except Exception as e:
        print_failure("FAILED!", out=sys.stdout)
        raise e

    print_success("SUCCESS!")

    if message:
        body = message.encode('utf-8')
    else:
        with open(file_path, 'rb') as f:
            body = f.read()
    channel = connection.channel()
    try:
        channel.basic_publish(exchange=exchange, routing_key=routing_key,
                              body=body, properties=properties)
    finally:
        channel.close()
    print_success("Message successfully published to exchange [%s]!"
                  % exchange)


@amqpcli.subcommand(name='config',
                    description='Configure the amqpcli client',
                    inherits=('nocolor',))
def amqp_config():
    pass


@amqp_config.subcommand(name='add_user',
                        description='Add a new queue user',
                        inherits=('nocolor',)
                        )
def amqp_add_user():
    new_user = input(Fore.GREEN + "User: " + Fore.RESET)
    new_pass = getpass(Fore.GREEN + "Password: " + Fore.RESET)
    new_vhost = input(Fore.GREEN + "vhost? [/]: " + Fore.RESET) or '/'
    USER_MAP['users'] = USER_MAP.get('users', {})
    USER_MAP['users'][new_user] = {}
    USER_MAP['users'][new_user]['vhost'] = new_vhost
    USER_MAP['users'][new_user]['password'] = new_pass
    USER_MAP.write()


@amqp_config.subcommand(name='delete_user',
                        description='Remove an existing queue user',
                        inherits=('nocolor',))
@clip.arg('user', name='user',
          help='User to delete',
          required=True)
def amqp_delete_user(user):
    users = USER_MAP.get('users', {})
    if user not in users:
        print_failure('No such user \'%s\' configured' % user)
        clip.exit(err=True)
    del users[user]
    USER_MAP.write()
    print_success("Configuration for user '%s' deleted" % user)


def main():
    try:
        app.run()
    except clip.ClipExit as e:
        sys.exit(e.status)

if __name__ == '__main__':
    main()
