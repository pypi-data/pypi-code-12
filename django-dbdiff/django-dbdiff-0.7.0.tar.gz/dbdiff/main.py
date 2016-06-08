import imp
import os
import sys

import django
from django.core.serializers import register_serializer


class Runner(object):
    def discover(self):
        from django.conf import settings
        for app in settings.INSTALLED_APPS:
            path = imp.find_module(app)

            for root, dirs, files in os.walk(path):
                print root,dirs, files

    def execute(self):
        pass


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
    import ipdb; ipdb.set_trace()
    django.setup()
    register_serializer('json', 'dbdiff.serializers.json')

    runner = Runner()
    runner.discover()
    runner.run()

if __name__ == "__main__":
    main()
