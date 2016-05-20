# -*- coding: utf-8 -*-
import os
import codecs
import glob
import datetime
import shutil
from string_utils import replace_str_by_dict_value


def append_file(base_file_path, append_file_path):
    base_file = codecs.open(base_file_path, 'a+', 'utf-8')
    append_file = codecs.open(append_file_path, 'r', 'utf-8')
    for line in append_file.readlines():
        base_file.write(line)
    base_file.close()
    append_file.close()


def get_file_lines(file_path):
    target_file = codecs.open(file_path, 'r', 'utf-8')
    lines = target_file.readlines()
    target_file.close()
    return lines


def get_file_line_cnt(file_path):
    cnt = 0
    with open(file_path, 'r') as f:
        for _ in f:
            cnt += 1
    return cnt


def grep_file(file_path, grep_str_list, output_file_path, file_code='utf-8', output_path='utf-8'):
    def chk_correspond(tmp_line):
        for grep_str in grep_str_list:
            if tmp_line.find(grep_str) == -1:
                return False
        return True
    target_file = codecs.open(file_path, 'r', file_code, errors='ignore')
    output_file = codecs.open(output_file_path, 'w', output_path)
    for line in target_file:
        if chk_correspond(line):
            output_file.write(line)
    target_file.close()
    output_file.close()


def get_file_timestamp(file_path):
    return datetime.datetime.fromtimestamp(os.stat(file_path).st_mtime)


def replace_file_contents(from_file_path, to_file_path, replace_dict):
    read_file = codecs.open(from_file_path, 'r')
    write_file = codecs.open(to_file_path, 'w')
    for line in read_file:
        line = replace_str_by_dict_value(line, replace_dict)
        write_file.write(line)
    read_file.close()
    write_file.close()


def get_dir_list(target_dir, include_hidden_folder=False):
    dir_list = []
    for dir_or_file_name in os.listdir(target_dir):
        if os.path.isdir(os.path.join(target_dir, dir_or_file_name)) is False:
            continue
        if include_hidden_folder is False and dir_or_file_name.startswith('.'):
            continue
        dir_list.append(dir_or_file_name)
    return dir_list


def get_file_path_list(target_folder_path, asc=True):
    file_path_list = glob.glob(target_folder_path + os.sep + '*.*')
    file_path_list.sort(cmp=lambda x, y: int(os.path.getmtime(x) - os.path.getmtime(y)), reverse=asc)
    return file_path_list


def make_dirs(dir_path):
    if os.path.isdir(dir_path) is False:
        try:
            os.makedirs(dir_path)
        except:
            pass


def interval_delete(target_folder_path, file_count):
    file_path_list = get_file_path_list(target_folder_path, True)
    for idx, file_path in enumerate(file_path_list):
        if idx < file_count:
            continue
        os.remove(file_path)


def interval_delete_folder(target_folder_path, leave_count):
    folder_list = get_dir_list(target_folder_path)
    folder_path_list = map(lambda n: os.path.join(target_folder_path, n), folder_list)
    folder_path_list.sort(cmp=lambda x, y: int(os.path.getmtime(x) - os.path.getmtime(y)), reverse=True)
    for idx, folder_path in enumerate(folder_path_list):
        if idx < leave_count:
            continue
        shutil.rmtree(folder_path)


def backup_file(file_path, target_dir):
    now = datetime.datetime.now()
    if os.path.isdir(target_dir) is False:
        os.makedirs(target_dir)
    backup_file_path = os.path.join(target_dir,
                                    os.path.basename(file_path) + '_' + now.strftime('%Y%m%d%H%M%S'))
    shutil.copyfile(file_path, backup_file_path)
