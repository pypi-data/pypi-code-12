import distutils.sysconfig
import re
import setuptools

site_packages_path = distutils.sysconfig.get_python_lib()
match = re.search(r'(lib[\\/](python\d+\.\d+[\\/])?site-packages)', site_packages_path, re.I)
relative_site_packages_path = match.group(1)

setuptools.setup(
    name = 'gevent-automonkey',
    version = '1.0.1',
    description = 'Automatically monkey patch a Python environment with gevent',
    url = 'https://github.com/schlarpc/gevent-automonkey',
    author = 'Chaz Schlarp',
    author_email = 'schlarpc@gmail.com',
    license = 'MIT',
    install_requires = ['gevent'],
    data_files = [
        (relative_site_packages_path, ['gevent_automonkey.pth']),
    ]
)
