import time
from ha_decorator import HaDecorator

@HaDecorator('192.168.99.100:2181')
def echo(args):
    print args
    time.sleep(1000)


if __name__ == '__main__':
    echo("test demo 2")
