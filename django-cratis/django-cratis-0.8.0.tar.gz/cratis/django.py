import sys

from cratis.env import load_env


def manage_command():
    load_env()

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
