from setuptools import setup, find_packages

setup(
    name = 'SBG_CWL_validation',
    packages = find_packages(), # this must be the same as the name above
    version = '0.1.8',
    description='Best practices validation of workflows and tools json files',
    author = 'Mohamed Marouf',
    author_email='mohamed.marouf@sbgenomics.com',
    keywords=['json', 'CWL', 'validation'],
    classifiers=[],
    entry_points = {'console_scripts':['SBG_CWL_validation = sbg_json_validation.json_validation:main']}
)
