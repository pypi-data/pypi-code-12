
import os
import sys
from distutils.sysconfig import get_python_lib
from setuptools import setup, find_packages

import work

# https://matthew-brett.github.io/pydagogue/installing_scripts.html
# http://click.pocoo.org/5/setuptools/
# http://foobar.lu/wp/2012/05/13/a-comprehensive-step-through-python-packaging-a-k-a-setup-scripts/

overlay_warning = False
if "install" in sys.argv:
    lib_paths = [get_python_lib()]
    if lib_paths[0].startswith("/usr/lib/"):
        # We have to try also with an explicit prefix of /usr/local in order to
        # catch Debian's custom user site-packages directory.
        lib_paths.append(get_python_lib(prefix="/usr/local"))
    for lib_path in lib_paths:
        existing_path = os.path.abspath(os.path.join(lib_path, "django"))
        if os.path.exists(existing_path):
            # We note the need for the warning here, but present it after the
            # command is run, so it's more likely to be seen.
            overlay_warning = True
            break

version = work.__version__

setup(
    name='simple_work',
    version=version,
    scripts=[],
    entry_points={
        'console_scripts': [
            'ovis3=work.scripts.ovis:main',
        ],
    },
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'Flask',
    ],
)
