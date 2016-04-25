from setuptools import setup, find_packages

version = '0.8.5'

setup(
    name='py3o.fusion',
    version=version,
    description="A Fusion server that will transform your "
                "py3o.template into final LibreOffice documents",
    long_description=open("README.rst").read(),
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Text Processing :: General",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    keywords='LibreOffice OpenOffice templating PDF Fusion',
    author='Florent Aide',
    author_email='florent.aide@gmail.com',
    url='http://bitbucket.org/faide/py3o.fusion',
    license='BSD License',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['py3o'],
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'setuptools',
        'py3o.template >= 0.9.9',
        'py3o.renderclient >= 0.2',
        'py3o.formats >= 0.3',  # we need native flags from 0.3
        'py3o.types >= 0.1',
        'twisted',
        'pygments',
    ],
    entry_points=dict(
        console_scripts=[
            'start-py3o-fusion = py3o.fusion.server:cmd_line_server',
        ],
    ),
)
