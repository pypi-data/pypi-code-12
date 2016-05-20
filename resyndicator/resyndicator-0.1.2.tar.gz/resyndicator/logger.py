import logging

logging.basicConfig(
    format='%(asctime)s: %(levelname)s:'
           ' %(funcName)s (%(thread)d):'
           ' %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
