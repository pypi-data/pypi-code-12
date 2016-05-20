from setuptools import setup, find_packages

setup(
    name = 'mafia_ops_tools',
    version = '0.5',
    keywords = ('ops', 'tools', 'server', 'ubuntu', 'op'),
    description = 'command line toolset to help you better manage servers.',
    license = 'MIT License',
    install_requires = [
    ],
    url = 'https://github.com/superluffy/ops_tools',
    author = 'yanbin',
    author_email = 'yanb1985@gmail.com',
    scripts=['netstatm.py', 'killcmd.py', 'sync_iterm_profile.py'],
    entry_points={
        'console_scripts': [
            'netstatm = netstatm:main',
            'killcmd = killcmd:main',
            'sync_iterm_profile = sync_iterm_profile:main',
        ],
    }
)
