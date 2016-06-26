import logging


def get_logger():
    logging.basicConfig()
    logger = logging.getLogger("najdisi_sms")
    logger.setLevel(logging.INFO)

    return logger
