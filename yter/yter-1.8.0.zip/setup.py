import setuptools
import re

readme = open("README.md").read()


setuptools.setup(
    name='yter',
    license='MIT',
    keywords='iterator itertools',
    description='Clever, quick iterators that make your smile whiter',

    author='Peter Shinners',
    author_email='pete at shinners.org',
    url='https://gitlab.com/shredwheat/yter',

    version=re.search(r"Version ([\d.]+)", readme).group(1),
    long_description=re.sub(r"\[(`.*?`)\]\(#.+?\)", r"\1", readme),

    packages=["yter"],

    zip_safe=True,
    tests_require=['pytest'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
    ],   # https://pypi.python.org/pypi?%3Aaction=list_classifiers
)
