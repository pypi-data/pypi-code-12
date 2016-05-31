from setuptools import setup, find_packages

setup(
    name = 'mtailf',
    version = '0.0.1',
    keywords = ('multiple tail', 'remote tail', 'tail'),
    description = 'use tail -f to multiple remote server',
    license = 'MIT License',
    install_requires = ['paramiko>=2.0'],
    entry_points={
        'console_scripts': [
            'mtailf = mtailf.mtailf:main',
        ],
    },
    author = 'skyleft',
    author_email = 'im@andy-cheung.me',
    packages = find_packages(),
    platforms = 'any',
)