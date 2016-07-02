from setuptools import setup

setup(
    name='on-tools',
    version='0.1',
    scripts=['src/scripts/check_migrations.py'],
    description='Opportunity Network Utilities',
    author='Rafal Zawadzki',
    author_email='rafal@opportunitynetwork.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
         'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development :: Build Tools'
        ],
)