from setuptools import setup, find_packages

setup(
    name='django-story-builder',
    version='0.1.2',
    author='John Leith',
    author_email='leith.john@gmail.com',
    packages=find_packages(),
    url='https://gitlab.com/leith-john/django-story-builder',
    description='Django project for creating CYOAs',
    install_requires=[
        "six", "admin-extra-urls", "markdown", "python-docx"
    ],
    include_package_data=True,
    zip_safe=False,
)
