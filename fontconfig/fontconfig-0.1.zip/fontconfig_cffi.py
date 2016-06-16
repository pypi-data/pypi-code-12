# Copyright (c) Marco Giusti
# See LICENSE for details.

import subprocess
import os.path
from cffi import FFI


def relopen(relpath, mode="r"):
    fullpath = os.path.join(os.path.dirname(__file__), relpath)
    return open(fullpath, mode)


def from_file(relpath):
    with relopen(relpath) as fp:
        return fp.read()


def parse_include(string):
    assert string.startswith("-I")
    return string[2:].strip()


def get_freetype_includes():
    cflags = subprocess.check_output(["freetype-config", "--cflags"])
    return map(parse_include, cflags.split())


ffi = FFI()
ffi.set_source("_fontconfig", from_file("_fixure.h"), libraries=["fontconfig"],
               include_dirs=get_freetype_includes())
ffi.cdef(from_file("_fontconfig.h"))
