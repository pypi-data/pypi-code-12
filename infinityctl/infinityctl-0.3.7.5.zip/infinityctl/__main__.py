import argparse
import sys
from distutils.spawn import _nt_quote_args

from . import update
from . import buildchange
from .startstop import start, stop
from .buildchange import build_change


def main():
    parser = argparse.ArgumentParser(prog='infinityctl', description='Инструмент для управления сервером Infinity.',
                                     argument_default=argparse.SUPPRESS)

    parser.add_argument('--quiet',
                        action='store_true',
                        help='отключить вывод')
    parser.add_argument('--version', '-v',
                        action='version',
                        version='%(prog)s 0.3.7.5')

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
    restart_parser = subparsers.add_parser("restart",
                                           help='перезапустить сервер')
    status_parser = subparsers.add_parser("status",
                                          help='статус сервера')
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
    args.func(args)

if __name__ == '__main__':
    main()
