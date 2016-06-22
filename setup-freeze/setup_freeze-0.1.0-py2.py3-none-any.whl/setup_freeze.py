#!/usr/bin/env python3

import subprocess
import ast
import re
from collections import defaultdict


class RequirementFinder(ast.NodeVisitor):
    def visit_Call(self, node):
        if node.func.id == 'setup':
            try:
                install_requires = next(x for x in node.keywords if x.arg == 'install_requires')
            except StopIteration:
                raise Exception("No setup_requires arg")

            requirement_list = defaultdict(list)

            for requirement in install_requires.value.elts:
                if isinstance(requirement, ast.Str):
                    requirement_list[requirement.lineno].append((requirement.col_offset, requirement.s))

            self.requirement_list = requirement_list
        else:
            return self.generic_visit(node)


def parse_requirement(requirement):
    return re.match(r'([^\[=<>!]+)(\[[^\]]\])?(<=|>=|==|!=|<|>)?(.+)?', requirement).groups()


def main():
    with open('setup.py', 'r') as f:
        setup_py_contents = f.read()

    pip_freeze = subprocess.check_output(('pip', 'freeze')).decode('utf8')
    package_list = [x.strip().split('==') for x in pip_freeze.split('\n') if x.find('==') != -1]
    package_map = {x[0].lower(): x[1] for x in package_list}

    the_ast = ast.parse(setup_py_contents, filename='setup.py')
    visitor = RequirementFinder()
    visitor.visit(the_ast)
    requirement_map = visitor.requirement_list

    setup_py_lines = setup_py_contents.split('\n')

    with open('setup.py', 'w') as f:
        for i, line in enumerate(setup_py_lines, start=1):
            offset = 0
            for col, item in requirement_map[i]:
                package, extras, comparison, version = parse_requirement(item)
                f.write(line[offset:col+1]) # include inital " symbol
                f.write(package)
                if extras:
                    f.write(extras)
                f.write('==')
                f.write(package_map[package.lower()])
                offset = col + len(item) + 1
            f.write(line[offset:])
            if i != len(setup_py_lines):
                f.write('\n')
