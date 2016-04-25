try:
    import multiprocessing
except ImportError:
    pass


from setuptools import setup

setup(
    name='Flask-Imagine',
    version='0.5',
    description='Extension which provides easy image manipulation support in Flask applications.',
    url='https://github.com/FlaskGuys/Flask-Imagine',

    author='Kronas',
    author_email='kronas.sw@gmail.com',
    license='MIT',

    packages=['flask_imagine', 'flask_imagine.adapters', 'flask_imagine.filters', 'flask_imagine.helpers'],

    install_requires=[

        'Flask>=0.9',
        'itsdangerous>=0.24',  # For Flask v0.9
        'Pillow==3.1.2',
        'six>=1.10.0',

    ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    zip_safe=False,
)
