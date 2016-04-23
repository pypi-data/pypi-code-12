#!/usr/bin/env python
import argparse
import lolcat


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file')

    args = parser.parse_args()

    with open(args.file, 'r+') as commitmsg:
        transformer = lolcat.LolCat()
        output = transformer.transform(commitmsg.read())
        commitmsg.seek(0)
        commitmsg.write(output)
        commitmsg.truncate()


if __name__ == '__main__':
    main()
