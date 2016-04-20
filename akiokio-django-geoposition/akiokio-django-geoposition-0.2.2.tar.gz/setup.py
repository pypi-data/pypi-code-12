from setuptools import setup, find_packages

setup(
    name='akiokio-django-geoposition',
    version=__import__('geoposition').__version__,
    description='Django model field that can hold a geoposition, and corresponding admin widget.',
    author='akiokio',
    author_email='akio.xd@gmail.com',
    url='http://github.com/akiokio/django-geoposition',
    download_url='https://github.com/akiokio/django-geoposition/tarbal/0.2.2',
    packages=find_packages(),
    zip_safe=False,
    package_data={
        'geoposition': [
            'locale/*/LC_MESSAGES/*',
            'templates/geoposition/widgets/*.html',
            'static/geoposition/*',
        ],
    },
    classifiers=[
      'Development Status :: 4 - Beta',
      'Environment :: Web Environment',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: BSD License',
      'Operating System :: OS Independent',
      'Programming Language :: Python',
      'Framework :: Django',
    ],
    install_requires=['django-appconf >= 1.0.2'],
)
