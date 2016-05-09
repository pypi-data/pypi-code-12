from distutils.core import setup

setup(
	name='GoTermAnalysis',
	version='0.2.3',
	author='Fan Yu',
	author_email='fay19@pitt.edu',
	packages=['gotermanalysis'],
	url='http://pypi.python.org/pypi/GoTermAnalysis/',
	long_description=open('README.txt').read(),
	description='Given lists of genes, find its associated gene ontology term enrichment and merge them up',
	install_requires=['MySQL-python', 'nltk', 'networkx', 'scipy'],	
	package_data = {
		# If any package contains *.txt or *.sql files, include them:
		'gotermanalysis': ['extra_file/*.txt', 'extra_file/*.sql', 'extra_file/*.jar' , 'extra_file/*.java', 'extra_file/*.class']},
	include_package_data=True,
)
