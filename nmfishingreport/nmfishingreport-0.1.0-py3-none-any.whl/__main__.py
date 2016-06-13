"""__main__.py

Provide an easy way to run nmfishingreport:

    python3 -m nmfishingreport -c config.ini
"""

import argparse

from . import internet_on
from . import nmfishingreport

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', default='config.ini', help="Config file "
                    "for nmfishingreport.py")
args = parser.parse_args()

if internet_on.internet_on():
    nmfishingreport.main(config_file=args.config)
