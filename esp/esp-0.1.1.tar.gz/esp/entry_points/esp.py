import argparse


def main():
    parser = argparse.ArgumentParser(prog='esp')
    subparser = parser.add_subparsers()
    external_accounts_parser = subparser.add_parser('add-external-account')
    external_accounts_parser.add_argument('external_account', help='Adds an external account', type=str)

    args = parser.parse_args()
    print(args)


if __name__ == '__main__':
    main()
