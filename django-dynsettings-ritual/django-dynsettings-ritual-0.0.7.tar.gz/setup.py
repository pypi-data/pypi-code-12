from setuptools import setup, find_packages

setup(
    name='django-dynsettings-ritual',
    version='0.0.7',
    namespace_packages=['grimoire', 'grimoire.django'],
    packages=find_packages(exclude=['dynsettings_proj', 'dynsettings_proj.*']),
    package_data={
        'grimoire.django.dynsettings': [
            'locale/*/LC_MESSAGES/*.*'
        ]
    },
    url='https://github.com/luismasuelli/django-dynsettings-ritual',
    license='LGPL',
    author='Luis y Anita',
    author_email='luismasuelli@hotmail.com',
    description='A Django application used to store dynamic settings (i.e. settings beyond the settings.py file), and retrieve them via another special object (instead of django.conf.settings, and wrapping it).',
    install_requires=['python-cantrips>=0.6.6', 'Django>=1.7', 'jsonfield>=1.0.3', 'django-polymorphic>=0.7']
)