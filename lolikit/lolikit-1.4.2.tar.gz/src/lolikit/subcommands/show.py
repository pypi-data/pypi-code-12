#########################################################################
#  The MIT License (MIT)
#
#  Copyright (c) 2014~2016 CIVA LIN (林雪凡)
#
#  Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated documentation files
#  (the "Software"), to deal in the Software without restriction, including
#  without limitation the rights to use, copy, modify, merge, publish,
#  distribute, sublicense, and/or sell copies of the Software, and to
#  permit persons to whom the Software is furnished to do so,
#  subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included
#  in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#  OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
#  CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
#  TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
#  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
##########################################################################


import argparse
import functools

from .. import command


class ShowCommand(command.Command):
    def get_name(self):
        return 'show'

    def register_parser(self, subparsers):
        subparsers.add_parser(
            self.get_name(),
            formatter_class=argparse.RawTextHelpFormatter,
            help='show current project\'s info',
            description='show current project\'s info')

    def run(self, args):
        def get_size_with_unit(size):
            """convert size bytes to other unit, return => (size, unit)"""
            units = ['Bytes', 'KB', 'MB', 'GB', 'TB']
            for unit in units:
                if len(str(int(size))) <= 4:
                    return (size, unit)
                else:
                    size = size / 1024
            return (size, units[-1])

        self.require_rootdir()

        md_total_size, md_total_size_unit = get_size_with_unit(
            self.__get_md_total_size())
        project_total_size, project_total_size_unit = get_size_with_unit(
            self.__get_project_total_size())
        info = '\n'.join([
            (' - Current Project Folder  =  {rootdir}'),
            (' - MD Count                = {md_count:>6,}'),
            (' - MD (Resourced) Count    = {rmd_count:>6,}'),
            (' - MD Avg. Depth           = {md_avg_depth:>9,.2f}'),
            (' - MD Total Size           = {md_total_size:>9,.2f}'
             ' {md_total_size_unit}'),
            (' - Project Total Size      = {project_total_size:>9,.2f}'
             ' {project_total_size_unit}'),
            ]).format(
                rootdir=str(self.rootdir),
                md_count=len(self.get_all_md_paths()),
                rmd_count=len(self.get_all_resourced_md_paths()),
                md_avg_depth=self.__get_md_avg_depth(),
                md_total_size=md_total_size,
                md_total_size_unit=md_total_size_unit,
                project_total_size=project_total_size,
                project_total_size_unit=project_total_size_unit,
                )
        print(info)

    def __get_md_total_size(self):
        """return md total size (bytes)"""
        return functools.reduce(
            lambda value, next: value + next.stat().st_size,
            self.get_all_md_paths(),
            0)

    def __get_project_total_size(self):
        """return project total size (bytes)"""
        return functools.reduce(
            lambda value, next: value + next.stat().st_size,
            (p for p in self.rootdir.rglob('*')),
            0)

    def __get_md_avg_depth(self):
        path_depths = [len(p.relative_to(self.rootdir).parents)
                       for p in self.get_all_md_paths()]
        # import collections
        # counter = collections.Counter(path_deeps)
        # print(sorted(counter.items(), key=lambda x: x[0]), )
        try:
            return sum(path_depths) / len(path_depths)
        except ZeroDivisionError:
            return 0
