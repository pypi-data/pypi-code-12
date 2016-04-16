import os
import logging

def write_text_to_file(filename, text):
    # Set up output dir
    wdir=os.path.abspath(os.path.dirname(__file__))

    # Set up the logger
    FORMAT = '%(asctime)-15s %(message)s'
    logging.basicConfig(format=FORMAT)
    logger = logging.getLogger('tcpserver')
    logger.setLevel(logging.DEBUG)

    with open(os.path.join(wdir, 'output', filename), 'w') as f:
        f.write(text)
        logger.debug("Wrote to %s" % filename)

