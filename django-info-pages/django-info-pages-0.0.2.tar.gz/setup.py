from setuptools import setup, find_packages
setup(
    name = "django-info-pages",
    version = "0.0.2",
    packages = find_packages(),
    author = "Edmund von der Burg",
    author_email = "evdb@ecclestoad.co.uk",
    url = "https://github.com/mysociety/django-info-pages",
    description = "Editable info pages and basic blog functionality for Django",
    license = "AGPL",
    keywords = "django blog cms",
    include_package_data=True,
    install_requires = [
        'Django>=1.8.12,<1.9',
        'beautifulsoup4',
        'lxml',
        'Markdown',
        'django-markitup',
        'nose',
        'django-autocomplete-light==2.3.3',
        'django-file-archive==0.0.2',
        'django-pagination==1.0.7',
        'django-slug-helpers==0.0.3',
    ],
    extras_require={
        'test': [
            'mock',
        ],
    },
)
