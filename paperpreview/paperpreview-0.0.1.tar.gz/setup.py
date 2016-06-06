from distutils.core import setup

setup(
    name='paperpreview',
    version='0.0.1',
    description='Create preview screenshot of your pdfs',
    url='https://github.com/sirrice/paperpreview',
    author='Eugene wu',
    author_email='ewu@cs.columbia.edu',
    packages=['paperpreview'],
    include_package_data=True,
    package_data={
    },
    scripts=['bin/paperpreview'],
    keywords=['latex', 'tex', 'pdf'],
    long_description='see http://github.com/sirrice/paperpreview',
    install_requires = [ 'click', 'wand' ]
)
