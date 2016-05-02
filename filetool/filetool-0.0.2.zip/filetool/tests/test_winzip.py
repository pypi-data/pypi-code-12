#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from filetool.winzip import (
    zip_a_folder, zip_everything_in_a_folder, zip_many_files)

#--- Unittest ---
if __name__ == "__main__":
    def test_zip():
        zip_a_folder(os.getcwd(), "1.zip")
        zip_everything_in_a_folder(os.getcwd(), "2.zip")
        zip_many_files([os.path.abspath("test_winzip.py")], "3.zip")

    test_zip()