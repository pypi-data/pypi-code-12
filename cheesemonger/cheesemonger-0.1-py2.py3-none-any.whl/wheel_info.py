from __future__ import print_function

import argparse
import os.path as pth

import distlib.wheel


def main():
    parser = argparse.ArgumentParser("wheel-info")
    parser.add_argument("wheel")

    args = parser.parse_args()

    whl = distlib.wheel.Wheel(
            pth.abspath(pth.expandvars(pth.expandvars(args.wheel))))

    for key, val in whl.info.items():
        print(key + ": " + val)


if __name__ == '__main__':
    main()
