import logging, json, datetime
from logging.handlers import DatagramHandler

host = '54.254.228.180'
port = 2435

class ChaikaHandler(DatagramHandler):

  def __init__(self, host='localhost', port=2435, service='unnamed', logType=None):
    super(ChaikaHandler, self).__init__(host, port)
    self.service = service
    self.logType = logType

  def makePickle(self, record):
    logTime = datetime.datetime.fromtimestamp(1462875627.825479).strftime('%Y-%m-%d %H:%M:%S.%f')
    """ Format for log like this 
    [2016-05-10 11:49:02.268] [DEBUG] [default] - Just a log for chaika-service, count: 1451
    """
    message = "[%s] [%s] [%s] - %s" % (logTime, record.levelname, record.name, record.msg + ' ' + " ".join(record.args))
    
    return bytes(json.dumps({
      'time': logTime,
      'logType': self.logType,
      'message': message,
      'level': record.levelname,
      'service': self.service,
      'catalog': '[%s]' % record.name
    },'utf-8'))

