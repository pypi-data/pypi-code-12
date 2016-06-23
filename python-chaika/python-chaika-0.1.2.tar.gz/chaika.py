import logging, json, datetime, traceback
from logging.handlers import DatagramHandler


class ChaikaHandler(DatagramHandler):

  def __init__(self, host='localhost', port=2435, service='unnamed', logType=None):
    super(ChaikaHandler, self).__init__(host, port)
    self.service = service
    self.logType = logType

  def makePickle(self, record):
    logTime = datetime.datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S.%f')
    tbs = []
    if record.exc_info is not None:
      tb = record.exc_info[2]
      tbs = traceback.format_tb(tb)
    """ Format for log like this 
    [2016-05-10 11:49:02.268] [DEBUG] [default] - Just a log for chaika-service, count: 1451
    """
    message = "[%s] [%s] [%s] - %s" % (logTime, record.levelname, record.name, r''.join(tbs) + record.msg + ' ' + " ".join(record.args))
    
    data = json.dumps({
      'time': logTime,
      'logType': self.logType,
      'message': message,
      'level': record.levelname,
      'service': self.service,
      'catalog': '[%s]' % record.name
    },'utf-8')
    return bytes(data)

