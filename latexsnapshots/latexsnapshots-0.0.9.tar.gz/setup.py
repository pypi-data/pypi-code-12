from distutils.core import setup

setup(
    name='latexsnapshots',
    version='0.0.9',
    description='Create snapshots of your latex papers + UI',
    url='https://github.com/sirrice/latexsnapshots',
    author='Eugene wu',
    author_email='ewu@cs.columbia.edu',
    packages=['latexsnapshots'],
    include_package_data=True,
    package_data={
      'latexsnapshots':['static/*.js', 'static/*.css', 'static/imgs/*', 'static/pdfs/*', 'templates/*']
    },
    scripts=['bin/latexsnapshots'],
    keywords=['latex', 'tex', 'pdf'],
    long_description='see http://github.com/sirrice/latexsnapshots',
    install_requires = [ 'click', 'sqlalchemy', 'Flask', 'wand', 'python-Levenshtein', 'gitpython' ]
)
