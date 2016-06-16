import argparse
import time


def get_downloader(uri, local_file, **kwargs):
    protocol = uri.split(':')[0]
    class_name = protocol.upper() + 'Downloader'
    module = __import__('pyDownloader.protocols.' + protocol, fromlist=class_name)
    downloader_class = getattr(module, class_name)

    downloader = None
    if len(kwargs.keys()) > 0:
        downloader = downloader_class(uri, local_file, **kwargs)
    else:
        downloader = downloader_class(uri, local_file)

    return downloader

if __name__ == '__main__':
    argument_parser = argparse.ArgumentParser(description='Download a file.')
    argument_parser.add_argument('uri', type=str)
    argument_parser.add_argument('local_file', type=str)

    arguments = argument_parser.parse_args()
    downloader = get_downloader(arguments.uri, arguments.local_file)

    downloader.download()

    while not downloader.completed():
        time.sleep(1)

    print 'File has been downloaded at: ' + arguments.local_file
