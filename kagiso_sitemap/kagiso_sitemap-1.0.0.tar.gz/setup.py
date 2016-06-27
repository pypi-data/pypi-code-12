from setuptools import find_packages, setup


setup(
    name='kagiso_sitemap',
    version='1.0.0',
    author='Kagiso Media',
    author_email='development@kagiso.io',
    description='Kagiso Sitemap',
    url='https://github.com/Kagiso-Future-Media/kagiso_sitemap',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'wagtail>=1.5.2',
    ]
)
