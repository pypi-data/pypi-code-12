from setuptools import setup, find_packages
import ast

version = "1.0.3"
desc = """A python module to provide decimal floating point arithmetic for complex numbers. 
Comes with many builtin functions such as powers and log."""
        
setup(
      name='complexdecimal',
      version=version,
      url = "https://github.com/Bowserinator/ComplexDecimal",
      description="Python Decimal support for complex Numbers",
      long_description = desc, 
      
      author='Bowserinator',
      author_email='bowserinator@gmail.com',
      license='GNU',
      packages=find_packages(),
      install_requires=[''],
      include_package_data=True,
      zip_safe=False
)
      
