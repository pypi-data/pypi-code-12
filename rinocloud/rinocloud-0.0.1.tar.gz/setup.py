from setuptools import setup
setup(
    name="rinocloud",
    version="0.0.1",
    packages=["rinocloud"],
    description='Rinocloud python bindings',
    author='Eoin Murray',
    author_email='eoin@rinocloud.com',
    url='https://github.com/rinocloud/rinocloud-python',  # use the URL to the github repo
    download_url='https://github.com/rinocloud/rinocloud-python/tarball/0.1',  # I'll explain this in a second
    keywords=['rinocloud', 'data', 'api'],  # arbitrary keywords
    classifiers=[],
    install_requires=[
        "requests",
        "requests_toolbelt",
        "arrow",
        "clint"
    ],
)
