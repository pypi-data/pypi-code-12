#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Arne Neumann <discourseinfostat.programming@arne.cl>

import discoursegraphs


def test_data_installation():
    """the `data` directory was installed properly with the package"""
    src_root_dir = discoursegraphs.SRC_ROOT_DIR
    package_root_dir = discoursegraphs.get_package_root_dir(src_root_dir)
    assert package_root_dir == discoursegraphs.get_package_root_dir()
    
    data_root_dir = discoursegraphs.DATA_ROOT_DIR

    print "SRC_ROOT_DIR:", src_root_dir
    print "PACKAGE_ROOT_DIR:", package_root_dir
    print "DATA_ROOT_DIR:", data_root_dir

    assert len(discoursegraphs.corpora.pcc) == 176


if __name__ == '__main__':
    test_data_installation()
