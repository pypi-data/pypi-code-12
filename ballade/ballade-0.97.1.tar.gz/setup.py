from setuptools import setup, find_packages


setup(
    name="ballade",
    version="0.97.1",
    license='https://opensource.org/licenses/MIT',
    description="A light weight http proxy based on tornado and an upstream proxy switcher using SwitchyOmega rules",
    author='holyshawn',
    author_email='holyshawn@outlook.com',
    url='https://github.com/holyshawn/ballade',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['tornado', 'pyyaml'],
    entry_points="""
    [console_scripts]
    ballade = ballade.startup:main
    """,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: Proxy Servers',
    ],
)
