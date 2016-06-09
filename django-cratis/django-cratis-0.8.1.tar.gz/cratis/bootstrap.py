import os
import string
from random import choice


def create_settings():
    if os.path.exists('settings.py'):
        print('settings.py already exists')
        return

    tpl = """
from cratis.settings import CratisConfig, CratisApplication as App


class Dev(CratisConfig):
    DEBUG = True
    SECRET_KEY = '%s'

    FEATURES = (
        # your features here
    )

App(locals()).setup()
""" % ''.join(choice(string.ascii_letters + string.digits) for _ in range(32))

    with open('settings.py', 'w+') as f:
        f.write(tpl)

    print('Ok. settings.py generated')


def run_env_command(command):
    return os.system('.pyvenv/bin/%s' % command)


def init_app(cratis_path=None, **kwargs):
    if not os.path.exists('.pyvenv'):
        os.system('pyvenv .pyvenv')

    if cratis_path:
        print(cratis_path)
        run_env_command('pip install -e %s[django]' % cratis_path)
    else:
        run_env_command('pip install django-cratis[django]')

    create_settings()