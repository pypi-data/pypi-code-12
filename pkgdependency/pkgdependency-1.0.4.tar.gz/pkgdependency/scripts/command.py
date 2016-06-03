# -*- coding:utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
import sys
from .. import verify_dependency


def main(argv=sys.argv):
    requirements_path = argv[1]
    verify_dependency(requirements_path, True)

if __name__ == '__main__':
    sys.exit(main() or 0)
