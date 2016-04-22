#!/usr/bin/env python

import json
import os
import sys
from markdown import markdown


IGNORED_NAMES = {".", ".."}


def notebook_walker(dir_path):
    for file_name in os.listdir(dir_path):
        first_letter = file_name[0]
        if file_name in IGNORED or first_letter == '.' or first_letter == '_':
            continue

        path = os.path.join(dir_path, file_name)
        if os.path.isdir(path):
            if first_letter != '.' and first_letter != '_':
                yield from phide_walker(path)
        else:
            if first_letter != '_' and file_name.endswith(".ipynb"):
                yield dir_path, path


def project_walker(base_dir):
    base_dir = os.path.abspath(base_dir)
    for path, name in notebook_walker(base_dir):
        project_path = os.path.abspath(path).replace(base_dir, "")
        yield project_path, name


def process_notebook_as_html(path):
    lines = []

    with open(path) as fp:
        notebook = json.load(fp)
    for cell in notebook["cells"]:
        cell_type = cell.get("cell_type")
        # TODO: REFACTOR THIS SLOP.
        if cell_type == "code":
            if "outputs" in cell:
                for output in cell["outputs"]:
                    if "data" in output:
                        data = output["data"]
                        if "image/svg+xml" in data:
                            lines.append("<div align='center'>")
                            lines.extend(data["image/svg+xml"])
                            lines.append("</div>")
        elif cell_type == "markdown":
            lines.append(markdown("\n".join(cell["source"])))
    return "".join(lines)

HEADER = """
<DOCTYPE html>
<html lang="en">
<head>
<title>Phide Simple HTML</title>
<style>
body{ font-size:10pt; font-family: Arial}
article { margin: 0 auto; width: 750px; line-height: 2; }
</style>
<head>
<body>
<article>
"""

FOOTER = """
</article></body></html>
"""

def compile_simple_html(base_dir, output_file, verbose=True):
    with open(output_file, 'w') as fp:
        fp.write(HEADER)
        for project_path, full_path in project_walker(base_dir):
            if verbose:
                print("Processing {}".format(full_path))
            fp.write(process_notebook_as_html(full_path))
        fp.write(FOOTER)

if __name__ == '__main__':
    if len(sys.argv) != 1:
        print("Usage: phide-paper-sync sync-dir")
        sys.exit(1)

    compile_simple_html(os.getcwd(), sys.argv[1])

