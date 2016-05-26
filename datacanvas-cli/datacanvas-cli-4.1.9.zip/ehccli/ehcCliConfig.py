import sys
import os
import ehcCliParser
import ConfigParser
import platform


class ehcCliConfig:
    def __init__(self):
      self.args = sys.argv[1:]
      self.parser = ehcCliParser.ehcCliParser()

    def ehcToken(self,token):
        p = ConfigParser.ConfigParser()
        system_m = platform.system()

        if 'Windows' in system_m:
            user_home = os.environ['HOMEPATH']
        else :
            user_home = os.environ['HOME']
        p.read(user_home +'/config_ehc.ini')
        fh = open(user_home +'/config_ehc.ini','w')
        p.set("config","token","%s"%token)
        p.write(fh)
        _token = p.get("config","token")
        return _token

    def ehcCookies(self,_cookies):
        p = ConfigParser.ConfigParser()
        system_m = platform.system()

        if 'Windows' in system_m:
            user_home = os.environ['HOMEPATH']
        else :
            user_home = os.environ['HOME']
        p.read( user_home +'/config_ehc.ini')
        fh = open(user_home +'/config_ehc.ini','w')
        p.set("config","cookies","%s"%_cookies)
        p.write(fh)
        _cookies = p.get("config","cookies")
        return _cookies

    def ehcPort(self,port):
        p = ConfigParser.ConfigParser()
        system_m = platform.system()

        if 'Windows' in system_m:
            user_home = os.environ['HOMEPATH']
        else :
            user_home = os.environ['HOME']
        p.read(user_home +'/config_ehc.ini')
        fh = open(user_home +'/config_ehc.ini','w')
        p.set("config","port","%s"%port)
        p.write(fh)
        _port= p.get("config","port")
        return _port

    def ehcHost(self,host):
        p = ConfigParser.ConfigParser()
        system_m = platform.system()

        if 'Windows' in system_m:
            user_home = os.environ['HOMEPATH']
        else :
            user_home = os.environ['HOME']
        p.read(user_home +'/config_ehc.ini')
        fh = open(user_home +'/config_ehc.ini','w')
        p.set("config","address","%s"%host)
        p.write(fh)
        _host= p.get("config","address")
        return _host





    def getToken(self):
        t = ConfigParser.ConfigParser()
        system_m = platform.system()

        if 'Windows' in system_m:
            user_home = os.environ['HOMEPATH']
        else :
            user_home = os.environ['HOME']
        t.read(user_home +'/config_ehc.ini')
        token = t.get("config","token")
        return token

    def getAddress(self):
        i = ConfigParser.ConfigParser()
        system_m = platform.system()

        if 'Windows' in system_m:
            user_home = os.environ['HOMEPATH']
        else :
            user_home = os.environ['HOME']
        i.read(user_home +'/config_ehc.ini')
        address = i.get("config","address")

        return address

    def getPort(self):
        a = ConfigParser.ConfigParser()
        system_m = platform.system()

        if 'Windows' in system_m:
            user_home = os.environ['HOMEPATH']
        else :
            user_home = os.environ['HOME']
        a.read(user_home +'/config_ehc.ini')
        port = a.get("config","port")
        return port

    def getCookies(self):
        a = ConfigParser.ConfigParser()
        system_m = platform.system()

        if 'Windows' in system_m:
            user_home = os.environ['HOMEPATH']
        else :
            user_home = os.environ['HOME']
        a.read(user_home +'/config_ehc.ini')
        cookies = a.get("config","cookies")
        return cookies