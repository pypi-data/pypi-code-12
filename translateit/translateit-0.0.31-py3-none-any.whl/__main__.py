import sys


def showhelp():
    help = """
    Usage: translate [word or sentence]
    """
    print(help)


def main(args=None):
    from .translate import tword
    if args is None:
        args = sys.argv[1:]

    if len(args) == 0:
        showhelp()
    else:
        tword(' '.join(args))

if __name__ == "__main__":
    main()
