from distutils.core import setup

setup(
    name='NBSVM',
    version='1.0',
    description='An implementation of NBSVM',
    long_description='An implementation of NBSVM. See http://nlp.stanford.edu/pubs/sidaw12_simple_sentiment.pdf',
    url='https://github.com/Joshua-Chin/nbsvm.git',
    author='Joshua Chin',
    author_email='JoshuaRChin@gmail.com',
    packages=['nbsvm'],
    install_requires=['scikit-learn', 'numpy']
)
