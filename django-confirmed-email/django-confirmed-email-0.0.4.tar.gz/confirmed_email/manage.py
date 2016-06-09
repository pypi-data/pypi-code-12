#!/usr/bin/env python
import os
import sys

package_parent_dir = os.path.normpath(
    os.path.join(os.path.abspath(__file__), os.path.pardir, os.path.pardir)
)
sys.path = [package_parent_dir] + sys.path
os.environ['DJANGO_SETTINGS_MODULE'] = 'confirmed_email.settings_test'

from django.conf import settings
from django.test import utils
from django.test.utils import get_runner


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "confirmed_email.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
