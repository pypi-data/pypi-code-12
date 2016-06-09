from distutils.core import setup
setup(
    name="parseoncolon",
    version="0.09",
    description='Simple parser of a strings where would keys and values are separated by a colon(:)',
    long_description=open('README.txt').read(),
    license='GPL',
    author='Eric Sammons',
    author_email='elsammons@gmail.com',
    url='https://bitbucket.org/elsammons/parseoncolon/overview',
    platforms=['linux', 'osx', 'win32'],
    py_modules=['parseoncolon'],
    keywords=['parse', 'strings', 'colon'],
    classifiers=[ ],
)
