"""Desired command line:

thriftplus --gen dart --base . --out /silver/pack/dart
thriftplus --gen py --base . --out /silver/pack/py
"""

import argparse
import collections
import os
import re
import shutil
import subprocess
import tempfile


def _all_thrift_paths(base_path):
    all_thrift_paths = []

    for root, _, files in os.walk(base_path):
        for file in files:
            if file.endswith('.thrift'):
                all_thrift_paths.append(os.path.join(root, file))

    return frozenset(all_thrift_paths)


class ThriftFile(object):
    _package_re = re.compile(r'^package\s+([a-z_.]+)$')
    _abs_import_re = re.compile(r'^import\s+([a-z_.]+)$')
    _local_import_re = re.compile(r'^import\s+([a-z_.]+)\s+as\s+([a-z_]+)$')
    _reference_re = re.compile(r'[a-z_.]+[.][a-zA-Z_][a-zA-Z_0-9]*')

    def __init__(self):
        self._path = None
        self._package = None
        self._imports = None
        self._body = None

    @staticmethod
    def _split_path_pieces(path):
        path_pieces = tuple(p.strip() for p in path.split('.'))

        if len(path_pieces) == 0:
            raise Exception('Invalid path')

        if any(p == '' for p in path_pieces):
            raise Exception('Invalid path')

        return path_pieces

    @staticmethod
    def _split_single_pieces(path):
        path_pieces = tuple(p.strip() for p in path.split('.'))

        if len(path_pieces) != 1:
            raise Exception('Invalid path')

        if path_pieces == '':
            raise Exception('Invalid path')

        return path_pieces

    @staticmethod
    def _split_body(body, imports, path):
        split_body = []
        imports_map = dict(imports)

        for line in body:
            start_pos = 0
            
            for match in ThriftFile._reference_re.finditer(line):
                if match.start() > start_pos:
                    split_body.append(('TEXT', line[start_pos:match.start()]))
                pathz = ThriftFile._split_path_pieces(match.group())
                pathzz = pathz[:-1]

                if pathzz not in imports_map:
                    raise Exception("Invalid import {} on '{}'".format(pathzz, path))

                split_body.append(('REF', imports_map[pathzz], pathz[-1]))
                start_pos = match.end()

            if len(line) > start_pos:
                split_body.append(('TEXT', line[start_pos:]))

        return split_body

    @staticmethod
    def parse(path, text_file):
        package = None
        imports = []
        in_body = False
        body = []

        for line in text_file:
            package_match = ThriftFile._package_re.match(line)

            if package_match is not None:
                if package is not None:
                    raise Exception('Multiple package definitions')

                if in_body:
                    raise Exception('Misplaced package line')

                package = package_match.group(1)
                continue

            abs_import_match = ThriftFile._abs_import_re.match(line)

            if abs_import_match is not None:
                if in_body:
                    raise Exception('Misplaced import line')

                imports.append((abs_import_match.group(1), abs_import_match.group(1)))
                continue

            local_import_match = ThriftFile._local_import_re.match(line)

            if local_import_match is not None:
                if in_body:
                    raise Exception('Misplaed import line')

                imports.append((local_import_match.group(2), local_import_match.group(1)))
                continue

            body.append(line)

        if package is None:
            raise Exception('No package line')

        thrift_file = ThriftFile()
        thrift_file._path = path
        thrift_file._package = ThriftFile._split_path_pieces(package)
        thrift_file._imports = tuple((ThriftFile._split_single_pieces(i), ThriftFile._split_path_pieces(j)) for (i,j) in imports)
        thrift_file._body = ThriftFile._split_body(body, thrift_file._imports, path)

        return thrift_file

    @property
    def path(self):
        return self._path

    @property
    def translated_path(self):
        return 'thriftgen_{}.thrift'.format('_'.join(self._package))

    @property
    def package(self):
        return self._package

    @property
    def package_symbol(self):
        return 'thriftgen_{}'.format('_'.join(self._package))

    @property
    def imports(self):
        return self._imports

    @property
    def body(self):
        return self._body

def _translate_thrift_file(gen, translated_thrift_file, thrift_file, thrift_files):
    ttf = translated_thrift_file

    ttf.write('// Package {}\n'.format(thrift_file.package_symbol))

    for import_ in thrift_file.imports:
        imported_thrift_file = thrift_files[import_[1]]
        ttf.write('include "{}"\n'.format(imported_thrift_file.translated_path))

    ttf.write('namespace {} {}\n'.format(gen, thrift_file.package_symbol))

    for body_part in thrift_file.body:
        if body_part[0] == 'TEXT':
            ttf.write(body_part[1])
        elif body_part[0] == 'REF':
            references_thrift_file = thrift_files[body_part[1]]
            ttf.write('%s.%s' % ((references_thrift_file.package_symbol, body_part[2])))
        else:
            raise Exception('Unknown body part')


class GenericGenerator(object):
    def generate(self, thrift_command, out, gen, thrift_path, thrift_file, thrift_files):
        final_thrift_path = os.path.join(out, thrift_file.package_symbol)
        if os.path.exists(final_thrift_path):
            shutil.rmtree(final_thrift_path)
        os.makedirs(final_thrift_path)
        subprocess.check_call([thrift_command, '-out', final_thrift_path, '--gen', gen, thrift_path])


class DartGenerator(object):
    def __init__(self):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'package.pubspec.yaml')) as pubspec_template_file:
            self._pubspec_template = pubspec_template_file.read()

    def generate(self, thrift_command, out, gen, thrift_path, thrift_file, thrift_files):
        final_thrift_path = os.path.join(out, thrift_file.package_symbol)
        if os.path.exists(final_thrift_path):
            shutil.rmtree(final_thrift_path)
        os.makedirs(final_thrift_path)
        subprocess.check_call([thrift_command, '-out', out, '--gen', 'dart', thrift_path])
        with open(os.path.join(final_thrift_path, 'pubspec.yaml'), 'w') as pubspec_file:
            pubspec_file.write(self._pubspec_template.format(
                    package_symbol=thrift_file.package_symbol,
                    import_dependencies='\n'.join('  {}: "0.0.0"'.format(thrift_files[i[1]].package_symbol) for i in thrift_file.imports),
                    import_overrides='\n'.join('  {p}:\n    path: ../{p}'.format(p=thrift_files[i[1]].package_symbol) for i in thrift_file.imports)))


class PythonGenerator(object):
    def __init__(self):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'package.setup.py')) as setup_template_file:
            self._setup_template = setup_template_file.read()

    def generate(self, thrift_command, out, gen, thrift_path, thrift_file, thrift_files):
        final_thrift_path = os.path.join(out, thrift_file.package_symbol)
        src_thrift_path = os.path.join(final_thrift_path, 'src')
        if os.path.exists(final_thrift_path):
            shutil.rmtree(final_thrift_path)
        os.makedirs(final_thrift_path)
        os.makedirs(src_thrift_path)
        subprocess.check_call([thrift_command, '-out', src_thrift_path, '--gen', 'py', thrift_path])
        os.remove(os.path.join(src_thrift_path, '__init__.py'))
        with open(os.path.join(final_thrift_path, 'setup.py'), 'w') as setup_file:
            setup_file.write(self._setup_template.format(
                    package_symbol=thrift_file.package_symbol,
                    import_dependencies=', '.join("'{}==0.0.0'".format(thrift_files[i[1]].package_symbol) for i in thrift_file.imports)))


GENERATORS = collections.defaultdict(
   lambda: GenericGenerator(),
   dart=DartGenerator(),
   py=PythonGenerator())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--gen', type=str, required=True,
        help='Generation target, same as for %%thrift%%')
    parser.add_argument('--base', type=str, required=True,
        help='Directory to use as root for searching for thrift files')
    parser.add_argument('--out', type=str, required=True,
        help='Directory where output packages will be placed')
    parser.add_argument('--thrift-command', type=str, default='thrift',
        help='Command to invoke for the Thrift compiler')
    args = parser.parse_args()

    thrift_paths = _all_thrift_paths(args.base)

    thrift_files = {}

    for thrift_path in thrift_paths:
        with open(thrift_path) as thrift_file:
            thrift_file = ThriftFile.parse(thrift_path, thrift_file)

            if thrift_file.package in thrift_files:
                raise Exception('Some packages are defined more than twice')

            thrift_files[thrift_file.package] = thrift_file

    for thrift_file in thrift_files.itervalues():
        for import_ in thrift_file.imports:
            if import_[1] not in thrift_files:
                raise Exception('Import "{}" in "{}" doest\'t exist'.format(import_[0], thrift_file.path))

    try:
        translated_dir_path = tempfile.mkdtemp()

        for thrift_file in thrift_files.itervalues():
            thrift_path = os.path.join(translated_dir_path, thrift_file.translated_path)
            with open(thrift_path, 'w') as translated_thrift_file:
                _translate_thrift_file(args.gen, translated_thrift_file, thrift_file, thrift_files)

        generator = GENERATORS[args.gen]

        for thrift_file in thrift_files.itervalues():
            thrift_path = os.path.join(translated_dir_path, thrift_file.translated_path)
            generator.generate(args.thrift_command, args.out, args.gen, thrift_path, thrift_file, thrift_files)
    finally:
        shutil.rmtree(translated_dir_path)
        

if __name__ == '__main__':
    main()

# TODO: argument order
