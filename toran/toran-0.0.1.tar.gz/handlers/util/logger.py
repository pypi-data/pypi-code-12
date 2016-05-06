import logging
import os


class Logger(object):
    def __init__(self, config_file):
        """
        Inits the logger according to the configuration passed
        :param Config config: config of the service
        :return: void
        """
        self.log_file = config_file
        logging.basicConfig(filename=self.log_file, level=logging.INFO)
        self.logger = logging.getLogger('gateway')
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.propagate = False
        self.logger.addHandler(file_handler)

    def get_logger(self):
        """
        returns this logger
        :return: self
        """
        return self.logger

    def log_http_info(self, environ, message='generic request info', request_id='', body_params=''):
        """
        Logs a default info from the gateway using environment data
        :param environ:
        :param message:
        :return:
        """
        self.get_logger().info(
            '' + environ.get('REQUEST_METHOD', '')
            + ' - ' + environ.get('HTTP_HOST', '')
            + ' - ' + environ.get('SERVER_PORT', '')
            + ' - ' + environ.get('PATH_INFO', '')
            + '?' + environ.get('QUERY_STRING', '')
            + ' - ' + message
            + ' - ' + request_id
            + ' - ' + body_params
        )

    def log_http_response(self, environ, code, request_id=''):
        """
        Logs a default info from the gateway using environment data
        :param message:
        :return:
        """
        self.get_logger().info(
            '' + environ.get('REQUEST_METHOD', '')
            + ' - ' + environ.get('HTTP_HOST', '')
            + ' - ' + environ.get('SERVER_PORT', '')
            + ' - ' + environ.get('PATH_INFO', '')
            + '?' + environ.get('QUERY_STRING', '')
            + ' - ' + 'Responding a request'
            + ' - ' + request_id
            + ' - ' + "{'code': '" + str(code) + "'}"
        )

    def log_gateway_error(self, message, detail, request_id, environ, error_type=500):
        self.get_logger().error(
            '' + environ.get('REQUEST_METHOD', '')
            + ' - ' + environ.get('HTTP_HOST', '')
            + ' - ' + environ.get('SERVER_PORT', '')
            + ' - ' + environ.get('PATH_INFO', '')
            + '?' + environ.get('QUERY_STRING', '')
            + ' - ' + message
            + ' - ' + request_id
            + ' - ' + str(error_type)
            + ' - ' + str(detail)
        )
