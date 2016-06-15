#!/Library/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Python
"""sorno_protobuf_to_dict.py converts text format of protobufs to python dict.

The script launches ipython for you to play with the parsed python dict.


    Copyright 2016 Heung Ming Tai

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
from pprint import pprint
import re
import sys

from sorno import debuggingutil
from sorno import sornomisc


class App(object):
    def __init__(self, args):
        self.args = args

    def run(self):
        with open(self.args.file) as f:
            content = f.read().strip()

        # combine all the fields into one protobuf that has the field "res" and
        # the field's value is the given protobufs read from the file
        obj_str = "res {\n%s\n}" % content

        # make any protobuf field key which has protobuf value to be a dict key
        # fld {...} => "fld": {...}
        obj_str = re.sub(r'(\S+) \{', r'"\1": {', obj_str)

        # make any non-protobuf field to be a dict key
        # fld: ... => "fld": ...
        obj_str = re.sub(r'([^\s"]+): ', r'"\1": ', obj_str)

        obj_str, s = protobuf_str_to_nested_list_str(obj_str, True)

        print("Your object before python eval:")
        print(obj_str)

        header = "Your object is in the variable: obj"
        header += "\nThe following functions are available: "
        functions = ("pprint",)
        header += ",".join(sorted(functions))

        protobuf = eval(obj_str)

        print("Your object before converting lists to python dict")
        pprint(protobuf)
        obj = protobuf_nested_ls_to_obj(protobuf)

        obj = obj.res

        debuggingutil.ipython_here(header=header)

        return 0


def protobuf_nested_ls_to_obj(mixed):
    if type(mixed) == list:
        if (type(mixed[0]) == list):
            return [protobuf_nested_ls_to_obj(protobuf) for protobuf in mixed]
        else:
            return sornomisc.Bunch(
                    **{
                        mixed[0]: process_protobuf_fields(mixed[1])
                    }
            )
    else:
        return mixed


def process_protobuf_fields(fields):
    d = {}
    for k, v in fields:
        if type(v) == list:
            processed = process_protobuf_fields(v)
        else:
            processed = v

        if k in d:
            if type(d[k]) == list:
                d[k].append(processed)
            else:
                d[k] = [d[k], processed]
        else:
            d[k] = processed

    return sornomisc.Bunch(**d)


def protobuf_str_to_nested_list_str(s, inside_protobuf):
    new_str = ""
    w = ""
    in_quote = False
    while s:
        c = s[0]
        if c == ":":
            if in_quote:
                w += c
            elif s.startswith(": {"):
                # we have a key in "w", and the value is a protobuf
                val, s = protobuf_str_to_nested_list_str(s[3:], True)
                new_str += ",[%s, [%s]]" % (w, val)
                w = ""
                continue
            else:
                # we have a key in "w", and the value is not protobuf
                val, s = protobuf_str_to_nested_list_str(s[2:], False)
                new_str += ",[%s, %s]" % (w, val)
                w = ""
                continue
        elif c == "}":
            if in_quote:
                w += c
            else:
                if w:
                    # we are at the last value of the last field of a protobuf
                    return w, s[1:]
                else:
                    # we are done with this protobuf
                    return new_str.lstrip(','), s[1:]
        elif c == '"':
            in_quote = not in_quote
            w += c
        elif c == ' ' or c == '\n':
            if in_quote:
                w += c
            elif w:
                if not inside_protobuf:
                    return w, s[1:]
        else:
            w += c

        s = s[1:]

    if w:
        new_str += w
    return new_str.lstrip(','), s


def parse_args(cmd_args):
    description = __doc__.split("Copyright 2016")[0].strip()

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "file"
    )

    args = parser.parse_args(cmd_args)
    return args


def main():
    args = parse_args(sys.argv[1:])

    app = App(args)
    sys.exit(app.run())


if __name__ == '__main__':
    main()
