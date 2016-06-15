#! /usr/bin/env python
"""
Creates a Django-Integrator compliant application, Django development project
and minnimal PyPI setup skeletons.
The django project app itself is named 'interface', as it holds the website
gateway interface file.
Please note that the default license is set to BSD.
"""
import argparse
from . import create

def main():
    """
    main function
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pypi_name',
        help='The name as it would be used in the PyPI repository.')

    parser.add_argument('django_app_class_name',
        help='The name class name as registered by Django.')

    parser.add_argument('verbose_name',
        help='The verbose name used in the Django admin and PyPI repository.')

    parser.add_argument('author',
        help='Your or your companies name.')

    parser.add_argument('email',
        help='Your or your companies email address.')

    args = parser.parse_args()
    tmp = {'name':args.pypi_name,
           'class':args.django_app_class_name,
           'verbose':args.verbose_name,
           'author':args.author,
           'email':args.email}

    create.main(tmp)

