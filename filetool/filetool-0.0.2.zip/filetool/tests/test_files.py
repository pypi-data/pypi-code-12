#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
filetool.files.py unittest
"""

import os
import unittest
from pprint import pprint as ppt
from filetool.files import WinFile, WinDir, FileCollection


class UnittestWinFile(unittest.TestCase):
    def setUp(self):
        self.winfile = WinFile("test.txt")
        
    def test_initialize(self):
        """测试WinFile多种初始化方式的实现。
        """
        level3_attributes = set([
            "abspath", "dirname", "basename", "fname", "ext",
            "atime", "ctime", "mtime", "size_on_disk", "md5",
        ])
        WinFile.set_initialize_mode(complexity=3)
        winfile = WinFile("test_files.py")
        attributes = set(winfile.to_dict())
        self.assertEqual(attributes, level3_attributes)

        level2_attributes = set([
            "abspath", "dirname", "basename", "fname", "ext",
            "atime", "ctime", "mtime", "size_on_disk",   
        ])
        WinFile.set_initialize_mode(complexity=2)
        winfile = WinFile("test_files.py")
        attributes = set(winfile.to_dict())
        self.assertEqual(attributes, level2_attributes)

        level1_attributes = set([
            "abspath", "dirname", "basename", "fname", "ext",
        ])
        WinFile.set_initialize_mode(complexity=1)
        winfile = WinFile("test_files.py")
        attributes = set(winfile.to_dict())
        self.assertEqual(attributes, level1_attributes)
        
        # 测试完毕, 恢复初始化模式为默认值
        WinFile.set_initialize_mode(complexity=2)

    def test_str_and_repr(self):
        winfile = WinFile("test_files.py")
        # print(repr(winfile))
    
    def test_rename(self):
        """测试文件重命名功能。
        """
        winfile = WinFile("test.txt")
        
        # 修改文件名为test1
        winfile.rename(new_fname="test1")
        d = winfile.to_dict()
        self.assertEqual(d["fname"], "test1")
        
        # 将文件名修改回test
        winfile.rename(new_fname="test")
        d = winfile.to_dict()
        self.assertEqual(d["fname"], "test")
    
    def test_copy(self):
        winfile1 = WinFile("test.txt")
        winfile2 = winfile1.copy()
        self.assertNotEqual(id(winfile1), id(winfile2))
        
    def test_copy_to_and_remove(self):
        winfile1 = WinFile("test.txt")
        winfile2 = winfile1.copy() # create a copy
        winfile2.update(new_fname="test-copy") # change file name
        
        self.assertFalse(winfile2.exists()) # not exists
        winfile1.copy_to(winfile2.abspath) # copy to new file
        self.assertTrue(winfile2.exists()) # now exists
        self.assertTrue(winfile2.isfile()) # now exists
        winfile2.delete() # delete the new file
        self.assertFalse(winfile2.exists()) # not exists
         
    
class UnittestWinDir(unittest.TestCase):
    def test_detail(self):
        windir = WinDir("testdir")
        # print(repr(windir))
    
    def test_rename(self):
        windir = WinDir("testdir")
        
        # 修改文件夹名为testdir1
        windir.rename(new_basename="testdir1")
        d = windir.to_dict()
        self.assertEqual(d["basename"], "testdir1")
        
        # 将文件夹名修改回testdir
        windir.rename(new_basename="testdir")
        d = windir.to_dict()
        self.assertEqual(d["basename"], "testdir")


class UnittestFileCollection(unittest.TestCase):
    def setUp(self):
        self._dir = "testdir"

    def test_yield_file(self):
        print("{:=^100}".format("yield_all_file_path"))
        for abspath in FileCollection.yield_all_file_path(self._dir):
            print(abspath)
             
        print("{:=^100}".format("yield_all_winfile"))
        for winfile in FileCollection.yield_all_winfile(self._dir):
            print(repr(winfile))
             
        print("{:=^100}".format("yield_all_top_file_path"))
        for abspath in FileCollection.yield_all_top_file_path(self._dir):
            print(abspath)
             
        print("{:=^100}".format("yield_all_top_winfile"))
        for winfile in FileCollection.yield_all_top_winfile(self._dir):
            print(repr(winfile))
            
    def test_from_path(self):
        fc = FileCollection.from_path(self._dir)
        basename_list = [winfile.basename for winfile in fc.iterfiles()]
        basename_list.sort() 
        expect = ["root_file.txt", "root_image.jpg", 
                  "sub_file.txt", "sub_image.jpg"]
        expect.sort()
        self.assertListEqual(basename_list, expect)
    
    def test_from_path_by_criterion(self):
        def image_filter(winfile):
            if winfile.ext in [".jpg", ".png"]:
                return True
            else:
                return False
            
        fc_yes, fc_no = FileCollection.from_path_by_criterion(
            self._dir, image_filter, keepboth=True)
        
        basename_list = [winfile.basename for winfile in fc_yes.iterfiles()]
        basename_list.sort()   
        expect_yes = ["root_image.jpg", "sub_image.jpg"]
        expect_yes.sort()
        self.assertListEqual(basename_list, expect_yes)
        
        basename_list = [winfile.basename for winfile in fc_no.iterfiles()]
        basename_list.sort()   
        expect_no = ["root_file.txt", "sub_file.txt"]
        expect_no.sort()
    
    def test_from_path_except(self):
        """测试from_path_except方法是否能正常工作。
        """
        fc = FileCollection.from_path_except(
            "testdir", ignore=["subfolder"])
        basename_list = [winfile.basename for winfile in fc.iterfiles()]
        basename_list.sort()        
        expect = ["root_file.txt", "root_image.jpg"]
        expect.sort()        
        self.assertListEqual(basename_list, expect)

        fc = FileCollection.from_path_except(
            "testdir", ignore_ext=[".jpg"])
        basename_list = [winfile.basename for winfile in fc.iterfiles()]
        basename_list.sort()        
        expect = ["root_file.txt", "sub_file.txt"]
        expect.sort()        
        self.assertListEqual(basename_list, expect)

        fc = FileCollection.from_path_except(
            "testdir", ignore_pattern=["image"])
        basename_list = [winfile.basename for winfile in fc.iterfiles()]
        basename_list.sort()
        expect = ["root_file.txt", "sub_file.txt"]
        expect.sort()
        self.assertListEqual(basename_list, expect)

    def test_from_path_by_pattern(self):
        """测试from_path_by_pattern方法是否能正常工作。
        """
        fc = FileCollection.from_path_by_pattern(
            "testdir", pattern=["sub"])
        basename_list = [winfile.basename for winfile in fc.iterfiles()]
        basename_list.sort()
        expect = ["sub_file.txt", "sub_image.jpg"]
        expect.sort()
        self.assertListEqual(basename_list, expect)

    def test_from_path_by_size(self):
        """测试from_from_path_by_size方法是否能正常工作。
        """
        fc = FileCollection.from_path_by_size("testdir", min_size=1024)
        basename_list = [winfile.basename for winfile in fc.iterfiles()]
        basename_list.sort()
        expect = ["root_image.jpg", "sub_image.jpg"]
        expect.sort()
        self.assertListEqual(basename_list, expect)
            
        fc = FileCollection.from_path_by_size("testdir", max_size=1024)
        basename_list = [winfile.basename for winfile in fc.iterfiles()]
        basename_list.sort()
        expect = ["root_file.txt", "sub_file.txt"]
        expect.sort()
        self.assertListEqual(basename_list, expect)

    def test_from_path_by_ext(self):
        """测试from_path_by_ext方法是否能正常工作。
        """
        fc = FileCollection.from_path_by_ext("testdir", ext=".jpg")
        basename_list = [winfile.basename for winfile in fc.iterfiles()]
        basename_list.sort()
        expect = ["root_image.jpg", "sub_image.jpg"]
        expect.sort()
        self.assertListEqual(basename_list, expect)
            
        fc = FileCollection.from_path_by_ext("testdir", ext=[".txt"])
        basename_list = [winfile.basename for winfile in fc.iterfiles()]
        basename_list.sort()
        expect = ["root_file.txt", "sub_file.txt"]
        expect.sort()
        self.assertListEqual(basename_list, expect)

    def test_from_path_by_md5(self):
        WinFile.set_initialize_mode(complexity=3)
        winfile = WinFile("test_files.py")
        WinFile.set_initialize_mode(complexity=2)
                     
        res = FileCollection.from_path_by_md5(os.getcwd(), winfile.md5)
        self.assertEqual(res[0].basename, "test_files.py")
 
    def test_add_and_remove(self):
        """测试添加WinFile和删除WinFile的方法是否正常工作。
        """
        fc = FileCollection()
        fc.add("test_files.py")
        self.assertEqual(fc.howmany, 1)
        fc.remove("test_files.py")
        self.assertEqual(fc.howmany, 0)
         
    def test_sort(self):
        """测试排序功能是否正常工作。
        """
        fc = FileCollection.from_path(self._dir)
        fc.sort_by_abspath()
        fc.sort_by_dirname()
        fc.sort_by_fname()
        fc.sort_by_ext()
        fc.sort_by_atime()
        fc.sort_by_ctime()
        fc.sort_by_mtime()
        fc.sort_by_size()
     
    def test_add(self):
        """测试两个集合相加是否正常工作。
        """
        fc1 = FileCollection.from_path(self._dir)
        fc2 = FileCollection.from_path(self._dir)
        fc3 = FileCollection()
        fc3.add("test_files.py")
         
        fc = fc1 + fc2 + fc3
        self.assertEqual(fc.howmany, 5)
         
        fc = FileCollection.sum([fc1, fc2, fc3])
        self.assertEqual(fc.howmany, 5)
 
    def test_sub(self):
        """测试两个集合相减是否正常工作。
        """
        fc1 = FileCollection.from_path(self._dir)
        fc2 = FileCollection.from_path(self._dir)
        fc = fc1 - fc2
        self.assertEqual(fc.howmany, 0)
     
    def test_create_fake_mirror(self):
        src = "testdir"
        dst = "testdir_mirror"
        FileCollection.create_fake_mirror(src, dst)
   
    def test_show_big_file(self):
        FileCollection.show_big_file(self._dir, 1000)
   
    def test_show_patterned_file(self):
        FileCollection.show_patterned_file(self._dir, ["image",])


#--- Unittest ---
if __name__ == "__main__":
    unittest.main()