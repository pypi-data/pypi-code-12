from setuptools import setup, find_packages

# I really prefer Markdown to reStructuredText. PyPi does not.
# from: https://coderwall.com/p/qawuyq/use-markdown-readme-s-in-python-modules
try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst', 'md')
    long_description = long_description.replace('\r','')
except (OSError, ImportError):
    print('Pandoc not found. Long_description conversion failure.')
    import io
    # pandoc is not installed, fallback to using raw contents
    with io.open('README.md', encoding='utf-8') as f:
        long_description = f.read()

# Setup the project
setup(
    name = 'pdml2flow',
    keywords = 'wireshark pdml flow aggregation',
    version = '1.2',
    packages = find_packages(),
    install_requires = [
        'dict2xml'
    ],
    # other arguments here...
    entry_points={
        'console_scripts': [
            'pdml2flow = pdml2flow:pdml2flow',
            'pdml2json = pdml2flow:pdml2json',
            'pdml2xml = pdml2flow:pdml2xml',
        ]
    },
    # metadata
    author = 'Mischa Lehmann',
    author_email = 'ducksource@duckpond.ch',
    description = 'Aggregates wireshark pdml to flows',
    long_description = long_description,
    include_package_data = True,
    license = 'Apache 2.0',
    url = 'https://github.com/Enteee/pdml2flow',
    # testing
    test_suite = 'test',
)
