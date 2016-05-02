import subprocess
import sys
import tempfile
import shutil
import os
import glob

from .util import print_status
from .config import Config


def update(args):
    config = Config()

    buildname = config.get_build(args.build)
    if not args:
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
        except FileNotFoundError:
            print_status("FAIL")
            print("Каталог " + builddir + " не найден")
            sys.exit(1)
        print_status("OK")
        sys.stdout.write("Восстановление конфигов")
        try:
            # восстановление конфигов из временного каталога
            shutil.copytree(tmpdir + "/config", builddir + "/config")
            shutil.copy(tmpdir + "/code/hub.dm",builddir + "/code/")
        except FileNotFoundError:
            print_status("FAIL")
            print("Каталог " + builddir + " не найден")
            sys.exit(1)
        print_status("OK")
    sys.stdout.write("Компиляция")
    # получаем все dme файлы и компилируем их
    projects = glob.glob(buildrepo + "/*.dme")
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