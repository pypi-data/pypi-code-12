from setuptools import setup, find_packages

setup(
    name = 'activegit',
    description = 'Uses git for distributed active learning',
    author = 'Casey Law, Umaa Rebbapragada',
    author_email = 'caseyjlaw@gmail.com',
    version = '0.37',
    url = 'http://github.com/caseyjlaw/activegit',
    packages = find_packages(),        # get all python scripts in real time
    install_requires=['sh', 'scikit-learn'],
    entry_points='''
        [console_scripts]
        aginit=activegit.cli:initrepo
        agclone=activegit.cli:clonerepo
'''

)
