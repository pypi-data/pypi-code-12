#!/usr/bin/env python
{imports}


{flask_global}
def main():
    import argparse
    parser = argparse.ArgumentParser()
{args}
    args = parser.parse_args()
{flask_main}


if __name__ == '__main__':
    main()
