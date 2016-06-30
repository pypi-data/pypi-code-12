# -*- coding: utf-8 -*-

import re
import os
import fnmatch
from pyATK.Misc.Misc import if_else


###
# List files within folder tree (generator)
#
def walkThroughFiles(top_dir, folder_filter="", file_filter=""):
    """
    >>> import os
    >>> walkThroughFiles(os.getcwd())
    <generator object walkThroughFiles at 0x...>
    >>> walkThroughFiles(os.getcwd(), 'src')
    <generator object walkThroughFiles at 0x...>
    >>> walkThroughFiles(os.getcwd(), '', '.py')
    <generator object walkThroughFiles at 0x...>
    """
    for dir_path, _, file_names in os.walk(top_dir):
        if folder_filter in dir_path:
            pass
        else:
            continue
        for file_name in file_names:
            if file_filter == "":
                yield os.path.join(dir_path, file_name)
            else:
                if fnmatch.fnmatch(file_name, file_filter) is True:
                    yield os.path.join(dir_path, file_name)


###
# List child folders of top directory (generator)
#
def walkThroughFolders(top_dir, folder_filter=""):
    """
    >>> import os
    >>> walkThroughFolders(os.getcwd())
    <generator object walkThroughFolders at 0x...>
    """
    for dir_path, _, _ in os.walk(top_dir):
        if folder_filter in dir_path:
            pass
        else:
            yield dir_path


###
# Returns the size of a folder's content. Returns 0 if the argument is not a folder
#
def folderSize(top_dir):
    """
    >>> import os
    >>> path = os.getcwd()
    >>> os.mkdir(os.path.join(path, 'test'))
    >>> folderSize(os.path.join(path, 'test'))
    0
    >>> file = open(os.path.join(path, 'test', 'tmp.txt'), 'w')
    >>> chars = file.write("Hello")
    >>> file.close()
    >>> folderSize(os.path.join(path, 'test'))
    5
    >>> folderSize('./not_found_folder')
    0
    >>> os.remove(os.path.join(path, 'test', 'tmp.txt'))
    >>> os.removedirs(os.path.join(path, 'test'))
    """
    if os.path.isdir(top_dir) is False:
        return 0
    else:
        total_size = 0
        for filename in walkThroughFiles(top_dir):
            total_size += os.path.getsize(filename)
        return total_size


def getAbsolutePath(relative_path):
    return os.path.abspath(relative_path)


def compareFiles(left, right):
    """
    >>> file = open('tmp.txt' ,'w')
    >>> file.close()
    >>> file = open('tmp2.txt', 'w')
    >>> file.close()
    >>> compareFiles('tmp.txt', 'tmp2.txt')
    0
    >>> file = open('tmp.txt', 'w')
    >>> chars = file.write('Hello')
    >>> file.close()
    >>> compareFiles('tmp.txt', 'tmp2.txt')
    -1
    >>> file = open('tmp2.txt', 'w')
    >>> chars = file.write('Hello World')
    >>> file.close()
    >>> compareFiles('tmp.txt', 'tmp2.txt')
    1
    """
    if not os.path.isfile(left):
        raise FileNotFoundError(str(left) + ": No such file or directory")
    if not os.path.isfile(right):
        raise FileNotFoundError(str(right) + ": No such file or directory")

    if os.path.getsize(left) == os.path.getsize(right):
        return 0
    else:
        with open(right, 'r') as right_file:
            right_content = right_file.read()
        with open(left, 'r') as left_file:
            left_content = left_file.read()

        if right_content > left_content:
            return 1
        return -1


def replaceInFile(filePath, pattern, replaceBy, caseSensitive=True):
    """
    >>> file = open('tmp.txt', 'w')
    >>> chars = file.write('Hello')
    >>> file.close()
    >>> replaceInFile('tmp.txt', 'Hello', 'World')
    >>> file = open('tmp.txt', 'r')
    >>> file.read()
    'World'
    """
    output = ""
    abs_path = getAbsolutePath(filePath)
    if os.path.isfile(abs_path):
        file = open(abs_path, 'r')
    else:
        raise IOError(abs_path + " is not a valid file")

    for line in file:
        output += re.sub(pattern, replaceBy, line, if_else(caseSensitive, 0, re.IGNORECASE))

    file.close()
    file = open(abs_path, 'w')
    if file:
        file.write(output)
    file.close()


def read_file_content(path, removeEmptyLines=False, encoding="utf-8"):
    """
    >>> data = read_file_content(__file__)
    >>> data = read_file_content(__file__, True)
    """
    abs_path = getAbsolutePath(path)
    file = open(abs_path, mode="r", encoding=encoding)
    if file:
        content = ""
        for line in file:
            if removeEmptyLines is True:
                if line != "":
                    content += line
            else:
                content += line
    else:
        raise FileNotFoundError(abs_path + "No such file or directory")
    return content

