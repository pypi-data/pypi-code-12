from setuptools import setup, find_packages
version = '0.1.15'

# try:
#     import pypandoc
#     read_md = lambda f: pypandoc.convert(f, 'rst')
# except ImportError:
#     print("warning: pypandoc module not found, could not convert Markdown to RST")
#     read_md = lambda f: open(f, 'r').read()
#
setup(
        name='mab',
        version=version,
        description="Multi-Armed Bandits Algorithms",
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Environment :: Console",
            "Intended Audience :: Developers",
            "Intended Audience :: Science/Research",
            "Natural Language :: English",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
            "Topic :: Utilities",
            "License :: OSI Approved :: MIT License",
            ],
        keywords='MAB, Multi-Armed Bandits, Machine Learning, Reinforcement Learning',
        author='Akihiko ITOH',
        author_email='itoh.akihiko.5@facebook.com',
        url='https://github.com/AkihikoITOH/MAB',
        license='MIT',
        packages=find_packages(exclude=['examples', 'tests', 'locals']),
        include_package_data=True,
        zip_safe=True,
        # long_description=read_md('README.md'),
        install_requires=['numpy', 'pypandoc'],
    )
