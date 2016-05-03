import os
from distutils.core import setup


README_FILE = os.path.join(os.path.dirname(__file__), 'README.md')

setup(
    name="PhIDE",
    version="0.0.4",
    packages=["phide"], # Basically, reserve that namespace.
    license="License :: OSI Approved :: MIT License",
    author="John Bjorn Nelson",
    author_email="jbn@abreka.com",
    description="An untested mess of tools for writing your Ph.D. in IPython",
    long_description=open(README_FILE).read(),
    data_files=['README.md'],
    scripts=['bin/phide-paper-sync.py',
             'bin/phide-simple-html.py'],
    install_requires=[
        "markdown"
    ],
    url="https://github.com/jbn/PhIDE"
)
