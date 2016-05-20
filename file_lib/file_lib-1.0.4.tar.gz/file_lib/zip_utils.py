# -*- coding: utf-8 -*-
import os
import zipfile
import subprocess


def compress(compress_file_path, target_dir):
    zip_file = zipfile.ZipFile(compress_file_path, 'w', zipfile.ZIP_DEFLATED)
    target_files = os.listdir(target_dir)
    for target_file in target_files:
        zip_file.write(os.path.join(target_dir, target_file), target_file)
    zip_file.close()
    return compress_file_path


def compress_files(compress_file_path, target_file_path_list):
    zip_file = zipfile.ZipFile(compress_file_path, 'w', zipfile.ZIP_DEFLATED)
    for target_file_path in target_file_path_list:
        zip_file.write(target_file_path, os.path.basename(target_file_path))
    zip_file.close()
    return compress_file_path


def decompress(decompress_file_path, target_dir):
    file_path_list = []
    with zipfile.ZipFile(decompress_file_path, 'r') as zip_file_obj:
        for name in zip_file_obj.namelist():
            zip_file_obj.extract(name, target_dir)
            file_path_list.append(os.path.join(target_dir, name))
    return file_path_list


def compress_file(compress_file_path, target_file_path):
    zip_file = zipfile.ZipFile(compress_file_path, 'w', zipfile.ZIP_DEFLATED)
    zip_file.write(target_file_path, os.path.basename(target_file_path))
    return compress_file_path


def compress_file_password(move_dir, compress_file_name, target_file_name, password):
    tmp = os.getcwd()
    os.chdir(move_dir)
    cmd = 'zip -P %s %s %s' % (password, compress_file_name, target_file_name)
    subprocess.call(cmd.strip().split(' '))
    os.chdir(tmp)


def compress_files_with_password(move_dir, compresses, zip_file_name, password):
    tmp = os.getcwd()
    os.chdir(move_dir)
    files = ' '.join(compresses)
    cmd = 'zip -P %s %s %s' % (password, zip_file_name, files)
    subprocess.call(cmd.strip().split(' '))
    os.chdir(tmp)


def decompress_file(decompress_file_path, target_dir, target_file):
    file_path = None
    with zipfile.ZipFile(decompress_file_path, 'r') as zip_file_obj:
        for name in zip_file_obj.namelist():
            if target_file != name:
                continue
            zip_file_obj.extract(name, target_dir)
            file_path = os.path.join(target_dir, name)
            break
    if file_path is None:
        raise Exception('not found compressed target file:{0}'.format(target_file))
    return file_path
