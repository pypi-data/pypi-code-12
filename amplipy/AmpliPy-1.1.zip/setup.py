from setuptools import setup, find_packages

setup(name="AmpliPy",
      version=1.1,
      description="A Python preprocessor",
      url="http://github.com/orangeflash81/amplipy",
      license="MIT",
      packages=find_packages(),
      install_requires=["astor", "colorama", "sphinx"],
      entry_points={"console_scripts": ['amplipy = amplipy.console:main']},
      keywords=["preprocessor", "lambda", "amplipy"],
      zip_safe=False)
