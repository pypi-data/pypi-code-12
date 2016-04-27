import sys

from findawspeers import FindAwsPeers


def main(args=sys.argv):
    """

    :param List[str] args:
    :return:
    """
    return FindAwsPeers.load(args).run()


if __name__ == '__main__':
    main()
