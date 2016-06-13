#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Import packages
from sys import exit
from os import chmod, remove, rename, getcwd, chdir, makedirs, walk, environ, chown, system
from os.path import abspath, dirname, join, isdir, isfile, exists, basename, splitext
from shutil import copyfile, copytree, rmtree, copy2
from tarfile import open
from pwd import getpwnam
from grp import getgrnam

class Utils:
    def __init__(self):
        self.path_list = []

    def get_current(self, file_path):
        return abspath(dirname(file_path))

    def exit(self):
        exit()

    def command(self, cmd):
        system(cmd)

    def pushd(self, path):
        self.path_list.append(getcwd())
        chdir(path)

    def popd(self):
        last_idx = len(self.path_list) - 1
        chdir(self.path_list[last_idx])
        del self.path_list[last_idx]

    def isfile(self, path):
        return isfile(path)

    def isdir(self, path):
        return isdir(path)

    def abspath(self, path):
        return abspath(path)

    def dirname(self, path):
        return dirname(path)

    def basename(self, path):
        return basename(path)

    def join_dirs(self, path_list):
        path = ""
        for idx in range(len(path_list)):
            path = join(path, path_list[idx])
        return path

    def get_env(self, key):
        return environ.get(key)

    def is_root(self):
        return (self.get_env("USER") == "root")

    def mkdir(self, path):
        if (not exists(path)):
            makedirs(path)

    def remove(self, path):
        if (isfile(path)):
            remove(path)
        elif (isdir(path)):
            rmtree(path)

    def rename(self, src, dst):
        if (exists(dst)):
            self.remove(dst)

        if (isfile(src)):
            rename(src, dst)
        elif (isdir(src)):
            self.remove(dst)
            self.copy(src, dst)
            self.remove(src)

    def splitext(self, path):
        return splitext(path)

    def get_file_path_in_dir(self, dir_path):
        path_list = []
        for (root, dirs, files) in walk(dir_path):
            for file_name in files:
                path_list.append(self.join_dirs([root, file_name]))
        return path_list

    def get_dir_path_in_dir(self, dir_path):
        path_list = []
        for (root, dirs, files) in walk(dir_path):
            for dir_name in dirs:
                path_list.append(self.join_dirs([root, dir_name]))
        return path_list

    def copy(self, src, dst):
        # file -> file(not exist)
        if (isfile(src) and isdir(dirname(dst)) and not isfile(dst)):
            copy2(src, dst)
        #file -> file(exist)
        elif (isfile(src) and isfile(dst)):
            self.remove(dst)
            copy2(src, dst)
        #dir -> dir(not exist)
        elif (isdir(src) and not isdir(dst)):
            copytree(src, dst)
        #dir -> dir(exist)
        elif (isdir(src) and isdir(dst)):
            src_len = len(src)
            path_list = self.get_file_path_in_dir(src)
            for path in path_list:
                src_relpath = path[src_len + 1:]
                dst_abspath = self.join_dirs([dst, src_relpath])
                src_abspath = self.join_dirs([src, src_relpath])
                if (isfile(dst_abspath)):
                    self.remove(dst_abspath)
                self.mkdir(dirname(dst_abspath))
                self.copy(src_abspath, dst_abspath)

    def chmod(self, path, mode):
        if (isfile(path) or isdir(path)):
            chmod(path, mode)

    def chown(self, path, user=None, group=None):
        if (user is None or group is None):
            print("Chown need user and group")
            exit()

        uid = getpwnam(user).pw_uid
        gid = getgrnam(group).gr_gid
        if (self.isfile(path)):
            chown(path, uid, gid)
        elif (self.isdir(path)):
            chown(path, uid, gid)
            for p in self.get_dir_path_in_dir(path):
                chown(p, uid, gid)
            for p in self.get_file_path_in_dir(path):
                chown(p, uid, gid)

    def decode(self, text):
        lookup = (
            'utf_8', 'euc_jp', 'euc_jis_2004', 'euc_jisx0213',
            'shift_jis', 'shift_jis_2004','shift_jisx0213',
            'iso2022jp', 'iso2022_jp_1', 'iso2022_jp_2', 'iso2022_jp_3',
            'iso2022_jp_ext','latin_1', 'ascii',
        )
        enc = None

        for encoding in lookup:
            try:
                text = text.decode(encoding)
                enc = encoding
                break
            except:
                pass
        if isinstance(text, unicode):
            return text, enc
        else:
            raise LookupError

    def unzip_tar(self, src, dst):
        tf = open(src)
        tf.extractall(dst)
        tf.close()

    def zip_tar(self, src, dst, mode):
        tf = open(dst, mode)
        for root, dirs, files in walk(src):
            for file_path in files:
                tf.add(self.join_dirs([root, file_path]))
        tf.close() 

    def unzip_tar_bz2(self, src, dst):
        self.unzip_tar(src, dst)

    def unzip_tar_gz(self, src, dst):
        self.unzip_tar(src, dst)

    def zip_tar_bz2(self, src, dst):
        self.zip_tar(src, dst, 'w:bz2')

    def zip_tar_gz(self, src, dst):
        self.zip_tar(src, dst, 'w:gz')
