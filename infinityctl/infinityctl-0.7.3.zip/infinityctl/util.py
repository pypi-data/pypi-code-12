import os
import shutil
import sys

from .config import Config


def print_status(T):
    (width, height) = shutil.get_terminal_size()
    if T == "OK":
        msg = "[\033[92m OK \033[0m]\n"
        sys.stdout.write(msg.rjust(23, '.'))
    elif T == "FAIL":
        msg = "[\033[91m FAIL \033[0m]\n"
        sys.stdout.write(msg.rjust(23, '.'))
    pass


def get_and_check_config(args):
    config = Config()

    buildname = config.get_build(args.get('build'))
    if not buildname:
        print('Указанный билд не найден')
        exit(1)
    builddir = config.basedir
    if not builddir:
        print('Базовая директроия не указана, проверьте конфиг.')
        sys.exit(1)
    buildrepo = config.basedir
    if not buildrepo:
        print('Базовая директроия не указана, проверьте конфиг.')
        sys.exit(1)

    builddir += buildname.get('folder')
    if not builddir or (builddir == config.basedir):
        print('Запись о каталоге не найдена. Проверьте конфиг.')
        sys.exit(1)
    buildrepo += buildname.get('repo')
    if not buildrepo or (buildrepo == config.basedir):
        print('Запись о репозитории не найдена. Проверьте конфиг.')
        sys.exit(1)

    if not os.path.exists(config.basedir):
        print('Базовый каталог, указанный в конфигурации не найден.')
        sys.exit(1)

    if not os.path.exists(builddir):
        print('Каталог билда не найден.')
        sys.exit(1)

    if not os.path.exists(buildrepo):
        print('Каталог репозитория билда не найден.')
        sys.exit(1)
    return config
