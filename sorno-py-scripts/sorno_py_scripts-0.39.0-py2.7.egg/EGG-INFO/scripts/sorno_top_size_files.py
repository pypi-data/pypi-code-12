#!/Library/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Python
"""Prints the top files in terms of sizes.

Prints the top files in terms of sizes under a directory or its subdirectories
in terms of the size


    Copyright 2014 Heung Ming Tai

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import argparse
from heapq import heappush, heappop, heapreplace
import os
import sys


class TopSizeFilesFinder(object):
    def __init__(self, num):
        """
        num - Top num files in terms of the size
        """
        self.num = num
        self.heap_size = num + 1

    def run(self, dirpath):
        heap = []

        join = os.path.join
        getsize = os.path.getsize

        for root, dirs, files in os.walk(dirpath):
            for f in files:
                filepath = join(root, f)
                size = getsize(filepath)
                self._add_to_heap(heap, filepath, size)

        # take out the items in heap which will not be included in the top
        # files
        while len(heap) > self.num:
            heappop(heap)

        # reverse the heap with a stack since it's a min heap
        stack = []
        while heap:
            stack.append(heappop(heap))

        num_size_digits = 0
        if stack:
            num_size_digits = len(str(stack[-1][0]))
        while stack:
            size, filepath = stack.pop()
            print("{0:{1}d}\t{2}".format(size, num_size_digits, filepath))

    def _add_to_heap(self, heap, filepath, size):
        if len(heap) < self.heap_size:
            heappush(heap, (size, filepath))
        else:
            heapreplace(heap, (size, filepath))


def parse_args(cmd_args):
    description = """
        Print the top files under a directory or its subdirectories in terms
        of the size
    """
    parser = argparse.ArgumentParser(
        description=description,
    )
    parser.add_argument(
        "path"
    )

    args = parser.parse_args(cmd_args)
    return args


def main():
    args = parse_args(sys.argv[1:])

    app = TopSizeFilesFinder(10)
    app.run(args.path)


if __name__ == '__main__':
    main()
