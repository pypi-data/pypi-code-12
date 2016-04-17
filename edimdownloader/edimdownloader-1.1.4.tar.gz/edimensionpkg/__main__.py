import edimensionpkg
from docopt import docopt
import edimdownloader

def main(args=None):
    EDException = edimdownloader.EDException
    USERNAME = None
    PASSWORD = None
    DIRNAME = None
    JSONFILE = "cache.json"

    doc_arguments = docopt(
        edimdownloader.__doc__,
        version="E Dimension Downloader " + edimensionpkg.__version__)

    if doc_arguments["--quiet"]:
        edimdownloader.QUIET = True

    if doc_arguments["<username>"]:
        USERNAME = doc_arguments["<username>"]
    else:
        if not USERNAME:
            raise EDException("USERNAME not found.")
    # check password exists
    if doc_arguments["<password>"]:
        PASSWORD = doc_arguments["<password>"]
    else:
        if not PASSWORD:
            raise EDException("PASSWORD not found.")
    # check dirname exists
    if doc_arguments["<dirname>"]:
        DIRNAME = doc_arguments["<dirname>"]
    else:
        if not DIRNAME:
            raise EDException("DIRNAME not found.")
    # check username exists
    if not JSONFILE:  # JSONFILE does not already exist
        JSONFILE = doc_arguments["-j"]
    else:
        if JSONFILE == "cache.json":  # If JSONFILE is the default
            JSONFILE = doc_arguments["-j"]

    with edimdownloader.EDimensionDownloader(USERNAME,
                                             PASSWORD,
                                             DIRNAME,
                                             JSONFILE) as ed:
        ed.run()


if __name__ == "__main__":
    main()
