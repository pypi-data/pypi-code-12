from setuptools import setup
import os

def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ''

setup(
    name='django-async-tasks',
    version=__import__('async_tasks').__version__,
    description=read('DESCRIPTION'),
    license='GNU General Public License (GPL)',
    keywords="task queue, job queue, async tasks, redis, python, django",
    author='Ivan Surov',
    author_email='ivansurovv@gmail.com',
    packages=['async_tasks'],
    install_requires=['redis', 'django-redis-cache'],
    include_package_data=True,
    long_description=read('README'),
    url='https://github.com/ivansurov/django-async-tasks',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)