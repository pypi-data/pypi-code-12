#!/usr/bin/python
# -*- encoding: utf-8 -*-
"""
    ipynb_format
    ~~~~~~~~~~~~

    Format the python code in a ipython notebook using yapf.

    :copyright: (c) 2016 by fg1
    :license: BSD, see LICENSE for more details
"""

__version__ = "0.1.0"

import os
import sys
import argparse

import IPython.nbformat.current as nbf
from yapf.yapflib.yapf_api import FormatCode
from yapf.yapflib.file_resources import GetDefaultStyleForDir


def ipynb_format(fname, style=None):
    f = open(fname, "r")
    nb = nbf.read(f, "ipynb")
    f.close()

    if style is None:
        style = GetDefaultStyleForDir(os.path.dirname(fname))

    modified = False
    for worksheet in nb["worksheets"]:
        for cell in worksheet["cells"]:
            if cell["cell_type"] != "code":
                continue
            if cell["language"] != "python":
                continue
            if len(cell["input"]) == 0:
                continue

            modcell = False
            out = []
            q = []
            for i in cell["input"].splitlines(True):
                if i.startswith("%"):
                    if len(q) > 0:
                        qf, mod = FormatCode("".join(q), style_config=style)
                        if mod:
                            modcell = True
                            out += qf.splitlines(True)
                        else:
                            out += q
                        q = []
                    out += [i]
                    continue
                q.append(i)

            if len(q) > 0:
                qf, mod = FormatCode("".join(q), style_config=style)
                if mod:
                    modcell = True
                    out += qf.splitlines(True)
                else:
                    out += q

            if len(out[-1]) == 0:
                modcell = True
                out = out[:-1]

            if out[-1][-1] == "\n":
                modcell = True
                out[-1] = out[-1][:-1]

            if modcell:
                cell["input"] = out
                modified = True

    if modified:
        f = open(fname, "w")
        nbf.write(nb, f, "ipynb")
        f.close()

    return modified


def cli():
    parser = argparse.ArgumentParser(description="Format ipython notebook using yapf")
    parser.add_argument("--style", action="store", help="yapf style to use")
    parser.add_argument("files", nargs="*")
    args = parser.parse_args()

    if len(args.files) == 0:
        parser.print_help()
        sys.exit(1)

    mod = False
    for f in args.files:
        mod |= ipynb_format(f, args.style)
    if mod:
        sys.exit(2)


if __name__ == "__main__":
    cli()
