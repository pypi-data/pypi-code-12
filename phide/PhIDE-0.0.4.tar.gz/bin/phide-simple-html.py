#!/usr/bin/env python

import os
from phide import (load_preferences, project_walker, generate_header,
                   process_notebook, build_html)


if __name__ == '__main__':
    cwd = os.getcwd()

    prefs = load_preferences(cwd)

    output_dir = os.path.join(cwd, "_phide_output")
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    media_dir = os.path.join(output_dir, "media")
    if not os.path.exists(media_dir):
        os.mkdir(media_dir)

    output_file = open(os.path.join(output_dir, "extract.md"), "w")

    output_file.write(generate_header(cwd, prefs))

    for project_path, full_path in project_walker(cwd):
        print("Processing: {}".format(full_path))
        process_notebook(full_path, output_dir, output_file)

    output_file.write("\n# Bibliography\n")
    output_file.close()
    build_html("_phide_output", "extract.md", "translation.html")

