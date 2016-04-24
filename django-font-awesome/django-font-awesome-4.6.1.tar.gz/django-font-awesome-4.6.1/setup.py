from setuptools import setup

setup(
    name='django-font-awesome',
    version='4.6.1',
    url='https://github.com/benbacardi/django-font-awesome',
    description='Font Awesome packaged in a django app to speed up new applications and deployment.',
    author='Ben Cardy',
    author_email='benbacardi@gmail.com',
    license='MIT',
    keywords='django staticfiles'.split(),
    platforms='any',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
    packages=['font_awesome'],
    package_data={'font_awesome': ['static/css/*', 'static/fonts/*']},
)
