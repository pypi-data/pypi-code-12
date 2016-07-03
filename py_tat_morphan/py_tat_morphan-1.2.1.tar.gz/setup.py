from setuptools import setup

setup(name='py_tat_morphan',
      version='1.2.1',
      description='Morphological Analyser for Tatar language',
      url='https://bitbucket.org/yaugear/py_tat_morphan/',
      author='Yaugear',
      author_email='ramil.gata@gmail.com',
      keywords=['morpological analyser', 'nlp', 'Tatar language'],
      license='MIT',
      packages=['py_tat_morphan'],
      scripts=['bin/tat_morphan_lookup',
               'bin/tat_morphan_process_text'],
      install_requires=[],
      include_package_data=True,
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False
     )
