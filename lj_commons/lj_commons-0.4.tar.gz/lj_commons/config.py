from ConfigParser import SafeConfigParser

parser = SafeConfigParser()
parser.read('mail_config.ini')

sender = parser.get('mail_config', 'sender')
print type(sender)
