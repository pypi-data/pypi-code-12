# Copyright 2014 ARM Limited
#
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

# standard library modules, , ,
from __future__ import print_function
from collections import defaultdict
import logging

# validate, , validate things, internal
from yotta.lib import validate

def addOptions(parser):
    parser.add_argument('--all', '-a', dest='list_all', default=False, action='store_true',
        help='List all licenses, not just each unique license.'
    )

def execCommand(args, following_args):
    c = validate.currentDirectoryModule()
    if not c:
        return 1

    if not args.target:
        logging.error('No target has been set, use "yotta target" to set one.')
        return 1

    target, errors = c.satisfyTarget(args.target)
    if errors:
        for error in errors:
            logging.error(error)
        return 1

    dependencies = c.getDependenciesRecursive(
                      target = target,
        available_components = [(c.getName(), c)]
    )

    errors = []
    if args.list_all:
        for name, dep in dependencies.items():
            if not dep:
                errors.append(u'%s is missing: license unknown!' % name)
            else:
                print(u'%s: %s' % (name, u', '.join(dep.licenses())))
    else:
        licenses = defaultdict(list)
        for name, dep in dependencies.items():
            if not dep:
                errors.append(u'%s is missing: license unknown!' % name)
            else:
                for lic in dep.licenses():
                    licenses[lic].append(name)
        for lic in licenses:
            print(lic)

    if len(errors):
        for err in errors:
            logging.error(err)
        return 1
    return 0

