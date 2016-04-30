import argparse
import logging
import inspect

from .main import convert_quiver_repo_to_rst


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('quiver_path', help='Path to Quiver repository.')
    parser.add_argument('output_path', help='Where to write output files.')
    parser.add_argument(
        '--timezone',
        dest='timezone_name',
        default='America/Los_Angeles',
        help='Timezone to use when interpreting dates stored in Quiver',
    )
    parser.add_argument(
        '--loglevel',
        default='INFO'
    )

    args = parser.parse_args()

    logging.basicConfig(level=logging.getLevelName(args.loglevel))

    acceptable_args = inspect.getargspec(convert_quiver_repo_to_rst).args
    convert_quiver_repo_to_rst(
        **{k: v for k, v in vars(args).items() if k in acceptable_args}
    )
