
import sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# typing library was introduced as a core module in version 3.5.0
requires = ["dirlistproc", "jsonasobj", "hcls-fhir-rdf>=0.1.3"]
if sys.version_info < (3, 5):
    requires.append("typing")

setup(
    name='fhir_to_sdo',
    version='0.2.0',
    packages=['fhir_to_sdo'],
    url='http://github.com/crDDI/fhir_to_sdo',
    license='Apache License 2.0',
    author='Harold Solbrig',
    author_email='solbrig.harold@mayo.edu',
    description='HL7 FHIR to schema.org conversion utility',
    long_description='Convert FHIR StructuredDefinitions and value sets into schema.org equivalents',
    install_requires=requires,
    scripts=['scripts/fhirtosdo'],
    classifiers=[
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only']
)
