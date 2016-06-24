#setup file

from setuptools import setup

setup(name='telomerehunter',
      version='1.0.4',
      description='Estimation of Telomere Content from WGS Data',
      long_description='TelomereHunter extracts, sorts and analyses telomeric reads from WGS Data. It is designed to take BAM files from a tumor and/or a control sample as input. The tool was developed at the German Cancer Research Center (DKFZ).',
      keywords='telomere content read NGS WGS tumor control',
      url='https://www.dkfz.de/en/applied-bioinformatics/telomerehunter/telomerehunter.html',
      author='Lars Feuerbach <l.feuerbach@dkfz-heidelberg.de>, Philip Ginsbach, Lina Sieverling <l.sieverling@dkfz-heidelberg.de>',
      author_email='l.sieverling@dkfz-heidelberg.de',
      license='GPL',
      packages=['telomerehunter'],
      install_requires=['pysam', 'PyPDF2'],
      include_package_data = True,
      scripts = ['bin/telomerehunter'],
      zip_safe=False)
