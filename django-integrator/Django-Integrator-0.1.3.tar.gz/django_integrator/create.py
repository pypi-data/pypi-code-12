"""
Creates a django_integrator compliant project.
"""
import os
import stat
import shutil
import sys
import time
import datetime
from django.core.management.commands import startproject

def _create_project(configuration):
    "create the project"
    command = startproject.Command()
    options = {'pythonpath': None, 'name': 'interface', 'files': [],
               'verbosity': 1, 'extensions': ['py'], 'no_color': False,
               'traceback': False, 'settings': None, 'template': None}
    options['directory'] = configuration['dir']
    command.handle(**options)

def _create_application(configuration):
    "create the application in the project."
    cmd = [sys.executable, os.path.join(configuration['dir'], 'manage.py'),
           'startapp', configuration['django_app_name']]
    os.popen(' '.join(cmd))


def _create_folders(configuration):
    "create folders"
    folders = ['documentation', 'models', 'tools', 'tests', 'views',
               os.path.join('management', 'commands'),]
    while not os.path.exists(configuration['django_app_name']):
        time.sleep(0.1)

    for folder in folders:
        os.makedirs(os.path.join(configuration['django_app_name'], folder))

def _copy_files(configuration):
    "copy template files"
    to_copy = [['admin_py.txt', 'admin.py'],
               ['init_py.txt', '__init__.py'],
               ['settings_py.txt', 'settings.py'],
               ['signals_py.txt', 'signals.py'],
               ['urls_py.txt', 'urls.py',],
               ['views_py.txt', 'views.py']]

    for source, target in to_copy:
        source = source = os.path.join(configuration['templates'], source)
        target = os.path.join(configuration['django_app_name'], target)
        if os.path.exists(target):
            os.remove(target)
        shutil.copy(source, target)

def _move_inits(configuration):
    "move modules that have the same name as the folder as an init to that dir."
    items = os.listdir(configuration['django_app_name'])
    for item in items:
        if item.lower().endswith('.py'):
            part = item[:-3].lower()
            if part in items:
                source = os.path.join(configuration['django_app_name'], item)
                target = os.path.join(configuration['django_app_name'], part,
                                      '__init__.py')
                os.rename(source, target)

def _make_inits_commands(configuration):
    "make the inits in the commands folder"
    items = [['management'], ['management', 'commands']]
    for row in items:
        row.insert(0, configuration['django_app_name'])
        row.append('__init__.py')
        with open(os.path.join(*row), 'w'):
            pass

def _make_contents_tools(configuration):
    "create the init and models module in the tools directory"
    with open(os.path.join(configuration['django_app_name'],
                           'tools', '__init__.py'), 'w'):
        pass

    source = os.path.join(configuration['templates'], 'models_py.txt')
    target = os.path.join(configuration['django_app_name'],
                          'tools', 'models.py')
    shutil.copy(source, target)


def _create_requirements(configuration):
    "Create the various requirements.txt files"
    # application requirements
    with open(os.path.join(configuration['django_app_name'],
                           'requirements.txt'), 'w') as file_write:
        file_write.write('django\n')

    # interface requirements
    with open(os.path.join('interface', 'requirements.txt'), 'w') as file_write:
        file_write.write('Django\ncoverage<4.0.0\npylint\nipython\n')
        file_write.write('django-integrator\n')

    # development requirements
    with open('requirements.txt', 'w') as file_write:
        file_write.write('-r interface/requirements.txt\n')
        file_write.write('-r application/requirements.txt\n')

def _copy_into_project(configuration):
    "Copy the files into the projects root."
    to_copy = [['README.txt', 'README.txt'],
               ['setup.cfg', 'setup.cfg']]

    for source, target in to_copy:
        source = source = os.path.join(configuration['templates'], source)
        target = os.path.join(target)
        shutil.copy(source, target)

def _append_integrator_imports(configuration):
    "Append to interface settings"
    with open(os.path.join('interface', 'settings.py'), 'a') as file_append:
        file_append.write('\n# Import applications\n')
        file_append.write('# pylint:disable=wrong-import-position\n')
        file_append.write('import django_integrator\n')
        text = "django_integrator.add_application('%s')\n"
        text = text % configuration['django_app_name']
        file_append.write(text)

    # Append to urls
    with open(os.path.join('interface', 'urls.py'), 'a') as file_append:
        file_append.write('\n# Add application urls\n')
        file_append.write('# pylint:disable=wrong-import-position\n')
        file_append.write('import django_integrator\n')
        file_append.write('django_integrator.add_urlpatterns(urlpatterns)')

def _write_devset(configuration):
    "write the developer reset."
    read_name = 'developer_reset_py.txt'
    write_name = 'devset.py'
    with open(os.path.join(configuration['templates'],
                           read_name), 'r') as file_read:
        text = ''.join(file_read.readlines())
        text = text.format(name=configuration['django_app_name'])
        with open(write_name, 'w') as file_write:
            file_write.write(text)

    os.chmod(write_name, stat.S_IEXEC|stat.S_IREAD)

def _write_license(configuration):
    "Write the license file"
    read_name = 'license_template.txt'
    write_name = 'LICENSE.txt'
    year = datetime.datetime.now().strftime('%Y')
    with open(os.path.join(configuration['templates'],
                           read_name), 'r') as file_read:
        text = ''.join(file_read.readlines())
        text = text.format(author=configuration['author'],
                           email=configuration['email'], year=year)
        with open(write_name, 'w') as file_write:
            file_write.write(text)

def _write_info(configuration):
    "Write the info file."
    read_name = 'info_py.txt'
    write_name = os.path.join(configuration['django_app_name'], '__info__.py')
    with open(os.path.join(configuration['templates'],
                           read_name), 'r') as file_read:
        text = ''.join(file_read.readlines())
        kwargs = {'class':configuration['class'],
                  'name':configuration['django_app_name'],
                  'verbose':configuration['verbose']}
        text = text.format(**kwargs)
        with open(write_name, 'w') as file_write:
            file_write.write(text)

def _write_setup(configuration):
    "Write the setup file."
    read_name = 'setup_py.txt'
    write_name = 'setup.py'
    with open(os.path.join(configuration['templates'],
                           read_name), 'r') as file_read:
        text = ''.join(file_read.readlines())
        text = text.format(**configuration)
        with open(write_name, 'w') as file_write:
            file_write.write(text)

PROCESS = [
    _create_project, _create_application, _create_folders, _copy_files,
    _move_inits, _make_inits_commands, _make_contents_tools,
    _create_requirements, _copy_into_project, _append_integrator_imports,
    _write_devset, _write_license, _write_info, _write_setup]

def main(configuration):
    "main functionality"
    cwd_original = os.path.abspath(os.getcwd())
    configuration['dir'] =  os.path.join(cwd_original,
                                         configuration['name'].strip().lower())
    os.mkdir(configuration['dir'])
    _ = os.path.dirname(os.path.abspath(__file__))
    configuration['templates'] = os.path.join(_, 'templates')

    _ = configuration['name'].lower().replace('-','_')
    configuration['django_app_name'] = _
    os.chdir(configuration['dir'])

    for function in PROCESS:
        function(configuration)

    os.chdir(cwd_original)
