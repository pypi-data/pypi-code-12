#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import copy
import fnmatch
from six import iteritems
import os
import requirements
import sys


def gt(first, second):
    """
    Compare two packages versions
    :param first: The first requirement
    :param second: Te second requirement
    :return: True if the first one is greater than the second
        or is the latest version
    """
    if not first.specs:
        return True
    if not second.specs:
        return False
    return first.specs[0][1] > second.specs[0][1]


def load_deps(filename):
    """
    Reads all the dependencies from a requirements file
    :param filename: The filename to load
    :return: A dict with the requirement name and the requirement object
    """
    reqs = dict()
    with open(filename, 'r') as req_file:
        lines = req_file.readlines()
        for line in lines:
            for req in requirements.parse(line):
                reqs.update({req.name.upper(): req})
    return reqs


def merge_requirements(merge_to, merge_from):
    """
    Takes a dict of requirements objects and merge
    :param merge_to: The first dict where you want to merge from
    :param merge_from: The second element where we want to merge from
    :return: A dict with the merged elements
    """
    res = copy.deepcopy(merge_to)
    for name, req in iteritems(merge_from):
        if name not in res or gt(req, res.get(name)):
            res.update({name: req})
    return res


def generate_merged_file(dest_file, path):
    file_list = search_reqs_files(path)
    for files in file_list:
        save_requirements(files, dest_file)


def save_requirements(requirementstxt, filename):
    """
    Take the requirements in the first file and save them to the second if they are
    newer or they're no present in the file
    :param requirementstxt: The requirements.txt file to parse
    :param filename: The file where all requirements will be saved
    :return: None. Just generates the file
    """
    if os.path.isfile(filename):
        fullreqs = load_deps(filename)
    else:
        fullreqs = dict()
    reqs = load_deps(requirementstxt)
    if not reqs:
        return
    fullreqs = merge_requirements(fullreqs, reqs)
    with open(filename, 'w') as req_file:
        for req in fullreqs.values():
            if req is not None:
                req_file.write(req.line+'\n')


def search_reqs_files(folder_name):
    """
    Searchs for all requirements.txt file recursively in the given path
    :param folder_name: the folder where you want to search
    :return: A list with all the files found, empty if none
    """
    res = list()
    for base, _, files in os.walk(folder_name):
        for file_name in fnmatch.filter(files, 'requirements.txt'):
            res.append(os.path.join(base, file_name))
    return res


def main(arguments):
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('dest_file', type=str,
                        help='The file where all requirements will be saved')
    parser.add_argument('--path', default='.', help='Path where to search')
    args = parser.parse_args(arguments)
    generate_merged_file(args.dest_file, args.path)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
