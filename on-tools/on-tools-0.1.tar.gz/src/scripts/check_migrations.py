"""Duplicated Django South migrations locator.
"""

import argparse
import subprocess
import re
import sys

def get_kev_value(line):
    """Extract key and value from the migration path.
    """
    key = '/'.join(line.split('/')[:-1])
    value = line.split('/')[-1:][0]
    return (key, value)

REGEXP = re.compile(r'^\d\d\d\d')
def get_number(migration_name):
    """Extract number from the migration number.
    """
    return REGEXP.findall(migration_name)[0]

def find_duplications(directory, strict=False):
    """Find the duplication in Django South migrations.
    """
    exit_code = 0
    process = subprocess.Popen(["find", directory, "-wholename",
                                "*migrations/0*py"],
                               stdout=subprocess.PIPE)
    stdout_value = process.communicate()[0].strip().decode('utf-8').split("\n")
    results = {}
    if stdout_value[0] == '':
        print("No migrations found at all")
        return exit_code

    for i in stdout_value:
        parsed = get_kev_value(i)
        migration_number = get_number(parsed[1])
        if parsed[0] in results:
            if migration_number in results[parsed[0]]:
                print("duplicated migration %s %s" % (parsed[0], parsed[1]))
                exit_code = -1
                if strict:
                    return exit_code
            else:
                results[parsed[0]].append(migration_number)
        else:
            results[parsed[0]] = [migration_number,]
    return exit_code

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Find duplicated Django South migrations.')
    parser.add_argument('directory', metavar='dir', type=str, nargs=1,
                        help='directory')
    parser.add_argument('--strict', action="store_true",
                        help='exit with error code when first duplicated migration found')
    args = parser.parse_args()
    sys.exit(find_duplications(args.directory[0], args.strict))
