from distutils.core import setup

setup(
    name = 'contextualized',
    py_modules = ['contextualized'],
    version = '1.3',
    description = 'Get tracebacks with context.',
    long_description=open('README.rst', 'rb').read().decode('UTF-8'),
    author='Juan Luis Boya García',
    author_email='ntrrgc@gmail.com',
    url = 'https://github.com/ntrrgc/contextualized',
    keywords = ['traceback', 'debugging'],
    license='MIT',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
