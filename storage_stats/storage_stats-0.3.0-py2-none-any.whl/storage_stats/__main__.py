# Copyright 2016 Peter May
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

__author__ = 'pmay'

import argparse
import storagestats as ss
import sys
from storage_stats import __version__

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    # Process CLI arguments #
    ap = argparse.ArgumentParser(prog="storage_stats",
                                 description="Calculates file size statistics for the specified folder.",
                                 epilog="MAPFILE should be a text file with one group of similar file"
                                        " extensions per line, separated by commas. Each line should be in"
                                        " lowercase and take the form: \".main_ext,.alt1,.alt2,etc\". For example: "
                                        "\".tiff,.tif\"")
    ap.add_argument("path", help="the folder to characterise")
    ap.add_argument("-e", dest="mapfile", default=None,
                    help="user file overriding similar extension mappings")
    ap.add_argument("-o", dest="output", help="CSV file to output statistics too")
    ap.add_argument("--no-recursion", dest="recursive", action="store_false",
                    help="do not include sub-folders in stats")
    ap.add_argument("--no-timing", dest="timing", action="store_false",
                    help="turn off preprocessing of directory to improve run-time (no timing information provided)")
    ap.add_argument("-s", "--silent", dest="silent", action="store_true",
                    help="turn off command line output (useful if you just want to output a CSV file")
    ap.add_argument("-v", "--version", action="version", version='%(prog)s v'+__version__, help="display program version")
    args = ap.parse_args()

    if args.path:
        # process the specified directory and print the stats
        characteriser = ss.Characteriser(args.mapfile)
        characteriser.process_directory(args.path, args.recursive, args.timing)

        if not args.silent:
            characteriser.print_stats()

        if args.output:
            characteriser.write_csv(args.output)

if __name__ == "__main__":
    main()
