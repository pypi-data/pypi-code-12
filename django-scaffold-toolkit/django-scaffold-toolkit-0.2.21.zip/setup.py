# coding=utf-8
import codecs

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import os
from setuptools import find_packages

base_dir = os.path.dirname(__file__)
setup(
    name='django-scaffold-toolkit',
    version='0.2.21',
    author='YuanXu',
    author_email='ankh2008@gmail.com',
    packages=['scaffold_toolkit'] + ['scaffold_toolkit.%s' % item for item in find_packages("scaffold_toolkit")],
    url="https://github.com/yuanxu/django-scaffold",
    license='LICENSE.txt',
    description=u'Django开发中一组常用工具。包括表单生成，验证，富文本编辑器，useragent检测等等',
    include_package_data=True,
    long_description=codecs.open(os.path.join(base_dir, 'README.md'), encoding='utf-8').read(),
    install_requires=[],  # ['django', 'requests', 'django-braces', 'shortuuid'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
        'Environment :: Web Environment',
        'Framework :: Django',
    ],
)
