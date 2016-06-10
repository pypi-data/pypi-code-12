import os
from setuptools import setup

def read(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read()

setup(
    name='slide2pdf',
    version='0.2',
    description='slide2pdf is a command line tool to convert html slide presenation to pdf',
    url='https://github.com/vengatlnx/slide2pdf',
    author='Vengatesh.S',
    author_email='vengat.lnx@gmail.com',
    license='MIT',
    packages=['slide2pdf'],
    install_requires=read('requirements.txt').splitlines(),
    zip_safe=False,
    entry_points={'console_scripts': ['slide2pdf=slide2pdf.command:main']}
    )
