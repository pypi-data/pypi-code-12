import os
import hashlib
import codecs
import configparser
import datetime
import subprocess
from contextlib import contextmanager
import jinja2
from python_boilerplate.inputs import *

__all__ = ['make_new']
basedir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(basedir))
license_alias = {
    'gpl': 'gpl3',
}


def write_template(template: str, namespace=None, ignore=False, path=None,
                   verbose=True, hash=None):
    """Render jinja template with the given namespace and saves it in the
    desired path"""

    if path is None:
        path = template

    template = jinja_env.get_template(template)
    data = template.render(**(namespace or {}))

    if os.path.exists(path) and ignore:
        return
    elif os.path.exists(path):
        with open(path) as F:
            filedata = F.read()
            if filedata == data:
                return

        # If hash is compatible with given hash, we simply overwrite
        ask = True
        if hash:
            filehash = hashlib.md5(filedata.encode('utf8')).digest()
            filehash = codecs.encode(filehash, 'base64').decode()
            if hash == filehash:
                os.rename(path, path + '.bak')
                ask = False

        if ask:
            msg = 'File %r exists. Save backup and overwrite?' % path
            response = yn_input(msg)
            if response == 'yes':
                os.rename(path, path + '.bak')
            else:
                return

    if verbose:
        print('    creating %s...' % os.path.abspath(path))

    with open(path, 'w') as F:
        F.write(data)

    return data


@contextmanager
def visit_dir(dir):
    """Visit directory and come back after the with block is finish."""

    currdir = os.getcwd()
    os.chdir(dir)
    yield
    os.chdir(currdir)


class BoilerplateConfig(configparser.ConfigParser):
    """A ConfigParser specialized in boilerplate.ini."""

    valid_attrs = ['project', 'author', 'email', 'version', 'license']

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.optionxform = str

        if os.path.exists('boilerplate.ini'):
            with open('boilerplate.ini') as F:
                self.read_file(F)

        # Create sessions
        if 'options' not in self:
            self.add_section('options')

        if 'file hashes' not in self:
            self.add_section('file hashes')

    def register_file(self, filename, data):
        """Compute and register the hash value for some file given its textual
        data."""

        filehash = hashlib.md5(data.encode('utf8')).digest()
        filehash = codecs.encode(filehash, 'base64').decode()
        self.set('file hashes', filename, filehash)

    def save(self):
        """Saves content to boilerplate.ini."""

        with open('boilerplate.ini', 'w') as F:
            self.write(F)


# noinspection PyAttributeOutsideInit
class ProjectFactory:
    """A new project job.

    Interacts with the user and keeps a common namespace for all sub-routines
    """
    def __init__(self, **kwds):
        self.basepath = os.getcwd()
        self.basepath_len = len(self.basepath)
        self.config = BoilerplateConfig()

        # Save values and use the default config
        for attr in BoilerplateConfig.valid_attrs:
            value = kwds.pop(attr, None)
            if value is None:
                value = self.config.get('options', attr, fallback=None)
            setattr(self, attr, value)

        if kwds:
            raise TypeError('invalid attribute: %s' % kwds.popitem()[0])

    def write_template(self, template, ignore=False, path=None):
        base = os.getcwd()
        file = os.path.join(base, path or template)
        file = file[self.basepath_len + 1:]

        # Prepare namespace
        namespace = vars(self).copy()
        del namespace['config']
        del namespace['basepath']
        del namespace['basepath_len']
        namespace['job'] = self
        namespace['date'] = datetime.datetime.now()

        # Write data and fetch hash
        data = write_template(template, namespace, ignore=ignore, path=path)
        if data is not None:
            self.config.register_file(file, data)

    def update(self, **kwargs):
        for arg, value in kwargs.items():
            if arg not in BoilerplateConfig.valid_attrs:
                raise AttributeError('invalid attribute: %r' % arg)
            setattr(self, arg, value)

    #
    # New project and new sections
    #
    def new_project(self, ask_editor=True):
        # Asks basic info
        if self.project is None:
            self.project = input("Project's name: ")
        if self.author is None:
            self.author = input("Author's name: ")
        if self.email is None:
            self.email = input("Author's email: ")

        # Fetch version from existing VERSION file or asks the user
        if self.version is None and os.path.exists('VERSION'):
            self.version = open('VERSION').read().strip()
        self.version = self.version or default_input("Version: ", '0.1.0')

        # Ask other input
        self.license = self.license or default_input('License: ', 'gpl')

        # Save config file
        self.save_config()
        if ask_editor:
            print('Your config file was saved as boilerplate.ini. You can '
                  'review  this file before proceeding. Please tell your '
                  'favorite editor or leave blank to continue.')
            editor = input('Editor: ').strip()
            if editor:
                subprocess.call([editor, 'boilerplate.ini'])
                self.__init__()
                return self.new_project(ask_editor=False)

        # Make each part of the source tree
        self.make_base(ignore=False)
        self.make_setup_py(ignore=False)
        self.make_package(ignore=False)
        self.make_docs(ignore=False)
        self.make_license(ignore=False)
        self.make_invoke(ignore=False)

    def make_base(self, ignore=True):
        self.write_template('VERSION.txt', ignore=True, path='VERSION')
        self.write_template('gitignore.txt', ignore=ignore, path='.gitignore')

    def make_setup_py(self, ignore=True):
        self.write_template('setup.py', ignore=ignore)
        self.write_template('MANIFEST.in', ignore=ignore)
        self.write_template('requirements.txt', ignore=ignore)
        self.write_template('requirements-dev.txt', ignore=ignore)

    def make_package(self, ignore=True):
        curdir = os.getcwd()
        try:
            # Make src/project directory
            for directory in ['src', self.project]:
                if not os.path.exists(directory):
                    os.mkdir(directory)
                os.chdir(directory)

            self.write_template('package/init.py', True, '__init__.py')
            self.write_template('package/__main__.py', ignore, '__main__.py')
            self.write_template('package/__meta__.py', True, '__meta__.py')

            # Make test folder
            if not os.path.exists('tests'):
                os.mkdir('tests')
            os.chdir('tests')

            if not os.path.exists('__init__.py'):
                with open('__init__.py', 'w') as F:
                    F.write('\n')
            self.write_template(
                'package/test_project.py', ignore, 'test_%s.py' % self.project)

        finally:
            os.chdir(curdir)

    def make_readme(self, ignore=True):
        self.write_template('README.rst', ignore=True)
        self.write_template('INSTALL.rst', ignore=ignore)

    def make_docs(self, ignore=True):
        self.make_readme(ignore=True)

        # Make src/project directory
        if not os.path.exists('docs'):
            os.mkdir('docs')
        self.write_template('docs/conf.py', ignore=ignore)
        self.write_template('docs/index.rst', ignore=ignore)
        self.write_template('docs/install.rst', ignore=ignore)
        self.write_template('docs/license.rst', ignore=ignore)
        self.write_template('docs/apidoc.rst', ignore=ignore)
        self.write_template('docs/warning.rst', ignore=ignore)
        self.write_template('docs/make.bat', ignore=True)
        self.write_template('docs/makefile.txt', ignore=True, path='Makefile')

        # Make sphinx folders
        with visit_dir('docs'):
            for folder in ['_static', '_build', '_templates']:
                if not os.path.exists(folder):
                    os.mkdir(folder)

    def make_license(self, ignore=True):
        license = license_alias.get(self.license, self.license)
        license_path = 'license/%s.txt' % license
        self.write_template(license_path, ignore=ignore, path='LICENSE')

    #
    # Features
    #
    def enable_feature(self, feature, **kwds):
        if not self.has_feature(feature):
            raise ValueError('invalid feature: %s' % feature)

        return getattr(self, 'make_' + feature)()

    def has_feature(self, feature):
        return feature in ['basic', 'docs', 'django']

    def make_basic(self, ignore=True):
        self.make_base(ignore)
        self.make_readme(ignore)
        self.make_setup_py(ignore)
        self.make_package(ignore)
        self.make_license(ignore)

    def make_django(self, ignore=True):
        pass

    def make_invoke(self, ignore=True):
        self.write_template('tasks.py', ignore)

    def save_config(self):
        for attr in BoilerplateConfig.valid_attrs:
            value = getattr(self, attr)
            if value is None:
                self.config.remove_option('options', attr)
            else:
                self.config.set('options', attr, value)


class attrdict(dict):
    """Dictionary with attribute access to keys."""

    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            raise AttributeError

    def __setattr__(self, attr, value):
        self[attr] = value

    def sub(self, keys):
        if isinstance(keys, str):
            keys = keys.split()
        return attrdict({k: self[k] for k in keys})


if __name__ == '__main__':
    dirname = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    root = os.path.dirname(dirname)
    os.chdir(os.path.join(root, 'playground'))
    print(os.listdir(os.getcwd()))

    if yn_input('clean?') == 'yes':
        os.system('rm * -Rv')

    factory = ProjectFactory(
        author='Chips', email='foo@bar', project='foobar', version='0.1',
        license='gpl')
    factory = ProjectFactory()
    print(dir(factory))
    factory.new_project()
