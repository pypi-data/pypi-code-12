from setuptools import setup

version = __import__('recipe').__version__

setup(name='sorinaso.recipe.redis',
      version=version,
      description="Redis recipe for buildout",
      long_description='',
      classifiers=[
        'Framework :: Buildout',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        ],
      keywords='buildout redis',
      author='Alejandro Souto',
      author_email='sorinaso@gmail.com',
      url='https://github.com/sorinaso/sorinaso.recipe.redis',
      license='MIT',
      packages=['recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires = ['hexagonit.recipe.cmmi'],
      entry_points = {'zc.buildout': ['default = recipe.redis:Recipe']},
)
