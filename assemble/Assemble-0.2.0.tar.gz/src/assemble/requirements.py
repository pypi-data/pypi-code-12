# -*- coding: utf-8 -*-
from Levenshtein import distance
from os import path
from os import walk
import ast
import pip
import pkgutil
import sys

IMPORT_IGNORE_PATH = path.dirname(ast.__file__)


def parse_ast(filename):
    with open(filename, 'rt') as stream:
        content = stream.read()

    return ast.parse(content, filename)


def scan_ast(root, ignore_paths):
    for node in ast.walk(root):
        if isinstance(node, ast.Import):
            modules = [n.name.split('.')[0] for n in node.names]
        elif isinstance(node, ast.ImportFrom):
            if not node.module:
                continue
            modules = [node.module.split('.')[0]]
        else:
            continue

        for module_name in modules:
            try:
                package = pkgutil.find_loader(module_name)
                if not package or not hasattr(package, 'filename'):
                    continue

                filename = package.filename

                c1 = not filename
                c2 = any(filename.startswith(i) for i in ignore_paths)
                c3 = module_name == filename
                if c1 or c2 or c3:
                    continue

                yield module_name
            except ImportError:
                pass


def scan_directory(where):
    sys.path.insert(0, where)
    module_names = set()

    for root, dirnames, pathnames in walk(where):
        pathnames = [f for f in pathnames if not f[0] == '.']
        dirnames[:] = [d for d in dirnames if not d[0] == '.']

        for pathname in pathnames:
            if not pathname.endswith('.py'):
                continue

            filename = path.join(where, root, pathname)
            node = parse_ast(filename)
            for module_name in scan_ast(node, [IMPORT_IGNORE_PATH, where]):
                if module_name not in module_names:
                    module_names.add(module_name)

    module_names = list(module_names)
    module_names = sorted(module_names, key=lambda k: k.lower())

    distributions = pip.get_installed_distributions()
    mapping = {}
    for distribution in distributions:
        mapping[distribution.project_name.lower()] = \
            str(distribution.as_requirement())

    def find_best_match(module_name):
        module_name = module_name.lower()
        if module_name in mapping:
            # module-name is the distribution
            return mapping[module_name]
        else:
            found = list()
            for distribution_name in mapping.keys():
                ld = distance(distribution_name, module_name)
                if module_name in distribution_name:
                    found.append([distribution_name, 0])
                elif ld < 3:
                    found.append([distribution_name, ld])

            if len(found):
                # sort on distance
                found.sort(key=lambda r: r[1])
                # return best matching
                return mapping[found[0][0]]
            else:
                # no match was found
                return None

    for module_name in module_names:
        yield module_name, find_best_match(module_name)

    assert sys.path.pop(0) == where
