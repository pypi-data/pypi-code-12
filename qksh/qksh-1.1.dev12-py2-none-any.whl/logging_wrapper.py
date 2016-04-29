import logging

# TODO: need to extend current logging module
# add support of notice level logging by super() method in __init__()
class Logger(object):

    def __init__(self, logger_lvl):
        """
        initial
        """

        NOTICE_LEVELV_NUM = 21
        log_path = '/var/log/qksh.log'

        logging.addLevelName(NOTICE_LEVELV_NUM, 'NOTICE')

        def notice(self, message, *args, **kws):

            if self.isEnabledFor(NOTICE_LEVELV_NUM):
                self._log(NOTICE_LEVELV_NUM, message, args, **kws)

        logging.Logger.notice = notice

        # TODO: logging level now hardcoded, need to be more flexible
        # logging.basicConfig(
        #     level=NOTICE_LEVELV_NUM,
        #     format='%(asctime)s %(levelname)s %(module)s'
        #            '[%(process)s]: %(message)s',
        #     datefmt="%Y-%m-%d %H:%M:%S",
        #     filename=log_path,
        #     filemode="a")

        fh = logging.FileHandler(log_path)
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            fmt='%(asctime)s %(levelname)s {} %(module)s[%(process)s]'
                ' line:%(lineno)d: %(message)s'.format(
                    logger_lvl.rsplit('.', 1)[1]),

            # remove line number in below log format
            # fmt='%(asctime)s %(levelname)s %(module)s[pid:%(process)s]'
            #     ' : %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')
        fh.setFormatter(formatter)
        self.logger = logging.getLogger(logger_lvl)
        self.logger.setLevel(logging.DEBUG)

        self.logger.addHandler(fh)
        self.logger.notice(logger_lvl)

    def debug(self, msg=""):
        """
        output DEBUG level LOG
        """
        self.logger.debug(str(msg))

    def info(self, msg=""):
        """
        output INFO level LOG
        """
        self.logger.info(str(msg))

    def notice(self, msg=""):
        """
        output INFO level LOG
        """
        self.logger.notice(str(msg))
        # logging.notice(str(msg))

    def warning(self, msg=""):
        """
        output WARN level LOG
        """
        self.logger.warning(str(msg))

    def exception(self, msg=""):
        """
        output Exception stack LOG
        """
        self.logger.exception(str(msg))

    def error(self, msg=""):
        """
        output ERROR level LOG
        """
        self.logger.error(str(msg))

    def critical(self, msg=""):
        """
        output FATAL level LOG
        """
        self.logger.critical(str(msg))


if __name__ == "__main__":
    testlog = Logger('')
    testlog.info("info....")
    testlog.warning("warning....")
    testlog.critical("critical....")
    testlog.notice("notice...")
    try:
        lists = []
        print lists[1]
    except Exception as ex:

        testlog.exception("execute task failed. the exception as follows:")
        testlog.info("++++++++++++++++++++++++++++++++++++++++++++++")

        testlog.error("execute task failed. the exception as follows:")
        exit(1)
