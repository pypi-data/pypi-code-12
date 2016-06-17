from distutils.core import setup

setup(
    version = '1.0.17',
    name = 'sapreprocessor',
    packages = ['sapreprocessor'],
    author_email='alxndr.psclt@gmail.com',
    license='MIT',
    url='http://sentiment-analysis-preprocessing-library.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
    
        # Indicate who your project is intended for
        'Intended Audience :: Developers',
    
        # Pick your license as you wish (should match "license" above)
         'License :: OSI Approved :: MIT License',
    
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
    ],
    #packages=find_packages(),
    #include_package_data = True,
    package_data={
            'sapreprocessor': ['data/wordlists/prefixs.json',
                               'data/wordlists/fr.json',
                               'data/lexicons/emojis_lexicon.json',
                               'data/lexicons/smileys_lexicon.json'
                               ]
    },
    install_requires=['langdetect', 'unidecode']
)


