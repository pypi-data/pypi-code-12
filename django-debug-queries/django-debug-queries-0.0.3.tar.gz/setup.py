from setuptools import setup, find_packages
setup(
    name = "django-debug-queries",
    version = "0.0.3",
    packages = find_packages(),
    author = "Mark Longair",
    author_email = "mark@mysociety.org",
    description = "A context manager for printing Django SQL queries to the terminal",
    license = "MIT",
    keywords = "django debugging sql debug queries",
    data_files = [("", ["LICENSE.txt"])],
    install_requires = [
        'Django',
    ]
)
