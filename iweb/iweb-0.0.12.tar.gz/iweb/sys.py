def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

class iWeb(object):

    def __init__(self, app):
        appConfig = AppConfig()
        appConfig.app = app

@singleton
class AppConfig(object):
    app = None

if __name__ == '__main__':
    from flask import Flask
    app = Flask(__name__)
    app.config['db'] = 'db'
    app.config['host'] = 'host'

    iweb = iWeb(app)

