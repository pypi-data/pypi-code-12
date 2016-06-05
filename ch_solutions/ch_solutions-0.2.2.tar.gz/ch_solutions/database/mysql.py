import socket
import pymysql
from pprint import pprint
from pymysql.err import OperationalError, ProgrammingError, InternalError
from ch_solutions.util.logger import get_logger


class MySQL:

    def __init__(self, host, user, password, db=None):
        self.db = None
        self.affected_rows = None
        self.host_name = host

        if db:
            self.db = pymysql.connect(host=host, user=user, password=password, db=db,
                                      cursorclass=pymysql.cursors.DictCursor)
        else:
            self.db = pymysql.connect(host=host, user=user, password=password,
                                      cursorclass=pymysql.cursors.DictCursor)

    def select(self, sql, values=None, one=False):
        log = get_logger('MySQl.select')
        log.debug('Attempting to select the following query on host: {0}'.format(self.host_name))
        log.debug('Query: {0}'.format(sql))
        if values:
            log.debug('Values: {0}'.format(values))
        try:
            with self.db.cursor() as cursor:
                if cursor.execute(sql, values):
                    if not one:
                        results = cursor.fetchall()
                        log.debug(pprint(results))
                        return results
                    else:
                        results = cursor.fetchone()
                        log.debug(pprint(results))
                        return results
                else:
                    # TODO: Make sure that we want to leave this as a false return instead of adjusting the logging.
                    log.debug('The query returned False')
                    return False
        except OperationalError as err:
            log.critical('There was an error while trying to query the database. Query: {0}'.format(sql))
            log.critical(err)
            raise
        except ProgrammingError as err:
            log.critical('The SQL query is malformed or incorrect.')
            log.critical(err)
            raise
        except InternalError as err:
            log.critical('There was an internal error.')
            log.critical(err)
            raise

    def execute(self, sql, values=None):
        log = get_logger('MySQl.execute')
        log.debug('Attempting to execute the following query on host: {0}'.format(self.host_name))
        log.debug('Query: {0}'.format(sql))
        if values:
            log.debug('Values: {0}'.format(values))
        try:
            with self.db.cursor() as cursor:
                if cursor.execute(sql, values):
                    affected_rows = cursor.commit()
                    self.affected_rows = affected_rows
                    log.debug('Query affected {0} rows'.format(self.affected_rows))
                    return True
                else:
                    log.debug('The Query returned false')
                    return False

        except OperationalError as err:
            log.critical('There was an error while trying to query the database. Query: {0}'.format(sql))
            log.critical(err)
            raise
        except ProgrammingError as err:
            log.critical('The SQL query is malformed or incorrect.')
            log.critical(err)
            raise
        except InternalError as err:
            log.critical('There was an internal error.')
            log.critical(err)
            raise

    def get_affected_rows(self):
        return self.affected_rows

    @staticmethod
    def test_mysql_host(host):
        log = get_logger('MySQL.test_mysql_host')
        log.debug('Building Socket')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            log.debug('Attempting to connect to {0} on port 3306'.format(host))
            sock.connect((host, 3306))
            sock.shutdown(2)
            log.info('{0}\'s mysql port is active and listening.'.format(host))
            log.debug('This does not guarantee that the service is operational')
            return True
        except:
            log.info('{0}\'s mysql port is not active or listening.'.format(host))
            return False
