# -*- coding: utf-8 -*-
import os
import gzip

EXT_GZIP = '.gz'


def un_gzip(file_path, output_file_path):
    with gzip.open(file_path, 'rb') as f_in:
        with open(output_file_path, 'wb') as f_out:
            f_out.writelines(f_in)
    f_out.close()


def compress_gzip(file_path, output_file_path=None):
    if output_file_path is None:
        o_path = file_path + EXT_GZIP
    else:
        o_path = output_file_path
    with open(file_path, 'rb') as f_in:
        with gzip.open(o_path, 'wb') as f_out:
            f_out.writelines(f_in)


def is_gzip(file_path):
    _, ext = os.path.splitext(file_path)
    if ext == EXT_GZIP:
        return True
    return False
