import argparse
import os

__author__ = 'user'

from subprocess import Popen


def configure_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base_url", action="store", default="http://10.150.250.73")
    parser.add_argument("--browser", action="store", default="firefox")
    parser.add_argument("--element_wait", action="store", default=10)
    parser.add_argument("--page_load_timeout", action="store", default=30)
    parser.add_argument("--element_init_timeout", action="store", default=0.2)
    parser.add_argument("--mysqlhost", action="store", default="10.150.250.73")
    parser.add_argument("--mysqluser", action="store", default="root")
    parser.add_argument("--mysqlpassword", action="store", default="toor")

    '''
    Параметр tests_root используется, когда нужно запустить отдельный тест (или модуль) в несколько потоков.
    Пример :
        запуск одного теста "--tests_root tests/test_auth.py::TestAuth::test_not_exist_login"
        запуск модуля "--tests_root tests/test_auth.py"
        запуск отдельного пакета "--tests_root tests/some_package/"
    '''
    parser.add_argument("--tests_root", action="store", dest="tests_root", default='tests')
    parser.add_argument("--days_from_current", action="store", dest="days_from_current", default=0)
    parser.add_argument("--threads", action="store", dest="threads", type=int, default=1)
    parser.add_argument("--alluredir", action="store")
    parser.add_argument("--python", action="store", dest="python", required=True)
    parser.add_argument("--attempts", action="store", dest="attempts", type=int, default=3)
    args = parser.parse_args()
    return args


def main():
    opt = configure_args()
    d = vars(opt)
    args = ''
    for key in d:
        if key not in ('threads', 'python'):
            args += '--' + key + ' \"' + str(d[key]) + '\" '

    processes = []
    if '.py' not in opt.tests_root:
        for root, directories, filenames in os.walk(opt.tests_root):
            '''
            в подкаталогах должны отсутствовать файлы с "__", например __init__.py
            '''
            if '__' not in root:
                for filename in filenames:
                    exec_string = opt.python + ' -m pytest %s %s' % (args, os.path.join(root, filename))
                    processes.append(exec_string.replace('\\', '/'))
    else:
        exec_string = opt.python + ' -m pytest %s %s' % (args, opt.tests_root)
        for num in range(0, opt.threads):
            processes.append(exec_string.replace('\\', '/'))

    launch = [processes[i:i + opt.threads] for i in range(0, len(processes), opt.threads)]

    for l in launch:
        treads = None
        for p in l:
            treads = Popen(p, shell=True)
        treads.communicate()

if __name__ == "__main__":
    main()
