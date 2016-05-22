import glob
import os
import shutil
import subprocess
import sys
import tempfile

from .startstop import start
from .util import print_status, get_and_check_config


def update(**args):
    config = get_and_check_config(args)
    build = config.get_build(args.get('build'))
    builddir = config.basedir + build.get('folder')
    buildrepo = config.basedir + build.get('repo')

    print("Обновление билда " + builddir + " " + "из " + buildrepo)

    sys.stdout.write("Обновление тестовой версии")
    try:
        if subprocess.call("git fetch", shell=True, cwd=buildrepo):
            print_status("FAIL")
            print("Возникла ошибка. Выход.")
            sys.exit(1)
    except FileNotFoundError:
        print_status("FAIL")
        print("Каталог " + buildrepo + " не найден")
        sys.exit(1)
    print_status("OK")
    sys.stdout.write("Слияние удаленной ветки с локальной")
    if subprocess.call(["git", "pull", "origin", "master"], shell=False, cwd=buildrepo):
        print_status("FAIL")
        print("Не удается слить ветки")
        sys.exit(1)
    print_status("OK")
    sys.stdout.write("Бэкап конфигов")
    # бэкапы файлов храним во временном каталоге в /tmp
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            if not os.path.isdir(tmpdir + "/code"):
                os.makedirs(tmpdir + "/code")
            shutil.copy(builddir + "/code/hub.dm", tmpdir + "/code/hub.dm")
            shutil.copytree(builddir + "/config/", tmpdir + "/config/")
            shutil.copytree(builddir + "/data/", tmpdir + "/data/")

        except FileNotFoundError:
            print_status("FAIL")
            print("Каталог " + builddir + " не найден")
            sys.exit(1)
        except:
            print_status("FAIL")
            print("Неизвестная ошибка")
            sys.exit(1)
        print_status("OK")
        sys.stdout.write("Копирование в основной билд")
        try:
            if os.path.exists(builddir):
                shutil.rmtree(builddir)
            shutil.copytree(buildrepo, builddir)
            # удалим каталог с конфигами. Все равно у нас есть бэкап
            shutil.rmtree(builddir + "/config")
            shutil.rmtree(builddir + "/data")
        except FileNotFoundError:
            print_status("FAIL")
            print("Каталог " + builddir + " не найден")
            sys.exit(1)
        print_status("OK")
        sys.stdout.write("Восстановление конфигов")
        try:
            # восстановление конфигов из временного каталога
            shutil.copytree(tmpdir + "/config", builddir + "/config")
            shutil.copytree(tmpdir + "/data", builddir + "/data")
            shutil.copy(tmpdir + "/code/hub.dm",builddir + "/code/")
        except FileNotFoundError:
            print_status("FAIL")
            print("Каталог " + builddir + " не найден")
            sys.exit(1)
        print_status("OK")
    sys.stdout.write("Компиляция")
    # получаем все dme файлы и компилируем их
    projects = glob.glob(builddir + "/*.dme")
    if not projects:
        print_status("FAIL")
        print("Файлы dme не найдены")
        sys.exit(1)
    if subprocess.call(["DreamMaker", projects[0]], shell=False, cwd=builddir):
        print_status("FAIL")
        print("Ошибка компиляции")
        sys.exit(1)
    print_status("OK")

    print("Обновление завершено!")

    if args.get('autostart'):
        print("Запуск сервера")
        start(args)
