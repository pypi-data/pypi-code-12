import logging

from . import downloader
from . import errors

LATEST = downloader.LATEST

DatasetError = errors.DatasetError
Downloader = downloader.Downloader

# Logging config
logger = logging.getLogger(__name__)


# Create a default downloader
downloader = Downloader(num_connections=4)

# Shortcut to default methods
get_path = downloader.get_path
is_downloaded = downloader.is_downloaded
