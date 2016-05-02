import sys
import json

DELIM = "\x01"


def main():
    keys = ["foo", "bar", "baz"]
    for line in sys.stdin:
        dct = json.loads(line)
        row = map(dct.get, keys)
        print DELIM.join(map(str, row))

    # Put some message on stderr
    sys.stderr.write("error message")
if __name__ == "__main__":
    main()
