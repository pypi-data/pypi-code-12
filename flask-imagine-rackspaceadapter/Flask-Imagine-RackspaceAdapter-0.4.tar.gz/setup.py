try:
    import multiprocessing
except ImportError:
    pass


from setuptools import setup

setup(
    name='Flask-Imagine-RackspaceAdapter',
    version='0.4',
    description='Rackspace Files adapter for Flask-Imagine extension.',
    url='https://github.com/FlaskGuys/Flask-Imagine-RackspaceAdapter',

    author='Kronas',
    author_email='kronas.sw@gmail.com',
    license='MIT',

    packages=['flask_imagine_rackspace_adapter'],

    install_requires=[

        'Flask-Imagine>=0.4',
        'boto>=2.38.0',

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
