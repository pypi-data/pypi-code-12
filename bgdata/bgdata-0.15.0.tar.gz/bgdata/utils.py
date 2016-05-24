import argparse
import logging
from http.client import HTTPConnection
from urllib.parse import urlparse
import sys

import bgdata

logger = logging.getLogger(__name__)


def check_url(url):
    p = urlparse(url)
    conn = HTTPConnection(p.netloc)
    conn.request('HEAD', p.path)
    resp = conn.getresponse()
    return resp.status < 400


def cmdline():

    # Parse the arguments
    parser = argparse.ArgumentParser()

    # Mandatory
    parser.add_argument('project', help='Project name')
    parser.add_argument('dataset', help='Dataset name')
    parser.add_argument('version', help='Dataset version')
    parser.add_argument('-b', '--build', default=bgdata.LATEST, help='Dataset build (default latest)')
    parser.add_argument('-v', '--verbose', dest='verbose', default=False, action='store_true', help="Give more information")
    parser.add_argument('-q', '--quiet', dest='quiet', default=False, action='store_true', help="Show only the path (useful to use in a bash script)")
    parser.add_argument('-n', '--num-connections', type=int, dest='num_connections', default=4, help="Specify maximum number of connections (default 4)")
    args = parser.parse_args()

    # Configure the logging
    if args.quiet:
        args.verbose = False

    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', datefmt='%H:%M:%S', level=logging.DEBUG if args.verbose else logging.INFO)
    logger.debug(args)

    # Create a downloader
    downloader = bgdata.Downloader(num_connections=args.num_connections)

    # Download the dataset
    try:
        dataset_path = downloader.get_path(args.project, args.dataset, args.version, build=args.build)
    except bgdata.DatasetError as e:
        logger.error(e.message)
        sys.exit(1)

    if not args.quiet:
        logger.info("Dataset downloaded")

    print(dataset_path)

if __name__ == "__main__":
    cmdline()

