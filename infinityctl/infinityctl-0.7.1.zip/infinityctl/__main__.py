import argparse
import sys

from . import update
from .buildchange import build_change
from .startstop import start, stop
from .status import status


def main():
    parser = argparse.ArgumentParser(prog='infinityctl', description='Инструмент для управления сервером Infinity.',
                                     argument_default=argparse.SUPPRESS)

    parser.add_argument('--version', '-v',
                        action='version',
                        version='%(prog)s 0.7.1')

    subparsers = parser.add_subparsers(help='Команды. Справка по команде: <команда> -h')

    start_parser = subparsers.add_parser("start", help='запустить сервер')
    start_parser.add_argument('--build',
                              '-b',
                              metavar='BUILD_NAME',
                              help='целевой билд',
                              default='tgstation',)
    start_parser.set_defaults(func=start)
    stop_parser = subparsers.add_parser("stop",
                                        help='остановить сервер')
    stop_parser.set_defaults(func=stop)

    status_parser = subparsers.add_parser("status",
                                          help='статус сервера')
    status_parser.set_defaults(func=status)

    update_parser = subparsers.add_parser("update",
                                          help='обновить сервер')
    update_parser.add_argument('--autostart', '-s',
                               action='store_true',
                               help='автозапуск')
    update_parser.add_argument('--build', '-b',
                               type=str,
                               default='tgstation',
                               help='билд для обновления (по умолчанию: tgstation)')
    update_parser.set_defaults(func=update.update)

    changemap_parser = subparsers.add_parser("map", help='сменить карту')
    changebuild_parser = subparsers.add_parser("changebuild", help='сменить билд')
    changebuild_parser.add_argument('--build',
                                    '-b',
                                    metavar='BUILD',
                                    help='целевой билд',
                                    required=True)
    changebuild_parser.set_defaults(func=build_change)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    args.func(**vars(args))

if __name__ == '__main__':
    main()
