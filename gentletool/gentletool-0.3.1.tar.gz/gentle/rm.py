#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
缓慢删除大文件
"""

"""
TODO: 完整verbose输出
TODO: 更好的human_time_cost实现
"""

import os
import sys
import traceback
import argparse
import logging
import re
from collections import namedtuple
import time

PY_VER = sys.version_info[0]
if PY_VER == 2:
    user_input = raw_input
if PY_VER == 3:
    user_input = input

Input = namedtuple('Input', ['block_size', 'verbose', 'files', 'stdin'])

logging.basicConfig(
    format='%(asctime)s %(levelname)s \n%(message)s\n', level=logging.INFO)
_LOGGER = logging.getLogger()

_BS_PAT = re.compile(
    pattern='^([0-9]+)([GgMmKk]?)([Bb]?)'
)
current_millisecond = lambda: int(round(time.time() * 1000))

KB = 1024
MB = 1024 * KB
GB = 1024 * MB

_DEFAULT_BLOCK_SIZE = 4096 * 512
_DEFAULT_SLEEP_INTERVAL = 0.1  # 单位是秒


def convert_human_bs_input(bs_string):
    """
    将输入的1G,1g,1M,1m,1K,1k
    转换成N bytes
    """
    match = re.match(_BS_PAT, bs_string)
    if not match:
        return 0
    nbytes, base, _ = match.groups()
    nbytes = int(nbytes)
    base = base.lower()
    if base == 'k':
        nbytes *= KB
    elif base == 'm':
        nbytes *= MB
    elif base == 'g':
        nbytes *= GB
    return nbytes


def parse_input():
    parser = argparse.ArgumentParser(
        description='Delete big file like a gentleman.')
    parser.add_argument('-bs',
                        required=False,
                        type=convert_human_bs_input,
                        default=_DEFAULT_BLOCK_SIZE,
                        help='每次删除的块大小，默认:{}'.format(_DEFAULT_BLOCK_SIZE))
    # parser.add_argument('--verbose',
    #                     action='store_true',
    #                     default=False,
    #                     help='verbose output')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--file', nargs='+', help='要删除的文件或文件列表')
    group.add_argument(
        '--stdin', default=False, action='store_true', help='从标准输入读取')

    try:
        args = parser.parse_args()
        return Input(block_size=args.bs, verbose=False, files=args.file, stdin=args.stdin)
    except IOError as e:
        traceback.print_exc()
        sys.exit(1)


def check_write_permission(filenames):
    """
    检查是否有可写的权限 
    返回：(可写列表，不可写列表，文件不存在列表)
    """
    writables = []
    not_writables = []
    not_found = []
    not_files = []
    for fname in filenames:
        if not os.path.exists(fname):
            not_found.append(fname)
        else:
            if not os.path.isfile(fname):
                not_files.append(fname)
            else:
                if os.access(fname, os.W_OK):
                    writables.append(fname)
                else:
                    not_writables.append(fname)
    return (writables, not_writables, not_found, not_files)


def human_size(fsize):

    if fsize > GB:
        return '{:.2f}GB'.format(float(fsize) / GB)
    elif fsize > MB:
        return '{:.2f}MB'.format(float(fsize) / MB)
    elif fsize > KB:
        return '{:.2f}KB'.format(float(fsize) / KB)
    else:
        return '{}B'.format(fsize)


def show_permission_result(writables, not_writables, not_found, not_files):
    """
    打印输入的文件信息
    """
    if not_files:
        _LOGGER.warning('####### 非文件列表\n{}'.format('\n'.join(not_files)))
    if not_found:
        _LOGGER.warning('####### 不存在的文件列表\n{}'.format('\n'.join(not_found)))
    if not_writables:
        _LOGGER.warning(
            '####### 没有写权限的文件列表\n{}'.format('\n'.join(not_writables)))
    if writables:
        units = []
        for fname in writables:
            fsize = os.stat(fname).st_size
            units.append('{0}\t{1}'.format(human_size(fsize), fname))
        _LOGGER.info('******* 可以删除的文件列表\n{}'.format('\n'.join(units)))


_SECOND = 1000
_MINUTE = 60 * _SECOND
_HOUR = 60 * _MINUTE


def human_time_cost(tc):
    """
    请毫秒单位的tc值，转换成人能看懂的时间字符串
    """
    tc = float(tc) / 1000
    return '{} 秒'.format(tc)


def gentle_delete_file(fname, block_size, verbose=False):
    begin = current_millisecond()
    st_size = os.stat(fname).st_size
    origin_size = st_size
    try:
        _LOGGER.info('正在删除文件{0}'.format(fname))
        fd = os.open(fname, os.O_RDWR)
        while st_size > 0:
            st_size -= block_size
            if st_size >= 0:
                os.ftruncate(fd, st_size)
            time.sleep(_DEFAULT_SLEEP_INTERVAL)
            # current_size = os.stat(fname).st_size
            # left_size_pct = float(current_size) / origin_size * 100
    except OSError as e:
        _LOGGER.error('删除文件{0}异常, {1}'.format(fname, str(e)))
    else:
        os.close(fd)
        os.unlink(fname)
        end = current_millisecond()
        time_cost = end - begin
        _LOGGER.info(
            '已经删除{0}, 耗时 {1} '.format(fname, human_time_cost(time_cost)))


def reduce_process_priority():
    os.nice(20)


def main():
    inputs = parse_input()
    filenames = []
    saved_stdin = sys.stdin
    if not inputs.stdin:
        filenames = inputs.files
    else:
        for line in saved_stdin:
            fname = line.replace('\n', '')
            if fname:
                filenames.append(fname)

    writables, not_writables, not_found, not_files = check_write_permission(
        filenames)
    show_permission_result(writables, not_writables, not_found, not_files)
    if not writables:
        _LOGGER.warning('没有可删除的文件, 拜拜~')
        sys.exit(0)

    sys.stdin = open('/dev/tty', 'r')
    confirm = user_input('------> 确定要删除吗？(Y/N, Yes/No): ')
    confirm = confirm.lower()
    if confirm == 'y' or confirm == 'yes':
        pass
    else:
        _LOGGER.warning('拜拜~')
        sys.exit(0)
    #恢复stdin
    sys.stdin = saved_stdin

    reduce_process_priority()

    # 依次删除文件
    for fname in writables:
        gentle_delete_file(fname, inputs.block_size, inputs.verbose)

    _LOGGER.info('拜拜~')


if __name__ == "__main__":
    main()
