import os
import ConfigParser
import ehcCliMain
import platform
def main():
    system_m = platform.system()

    if 'Windows' in system_m:
        user_home = os.environ['HOMEPATH']
        a = os.path.exists(user_home +'/config_ehc.ini')
    else :
        user_home = os.environ['HOME']
        a = os.path.exists(user_home +'/config_ehc.ini')
    if a == False:
        conf = open(user_home +'/config_ehc.ini','w')
        config_write = ConfigParser.ConfigParser()
        config_write.add_section('config')
        config_write.set('config','address','')
        config_write.set('config','port','')
        config_write.set('config','token','')
        config_write.set('config','cookies','')
        config_write.write(conf)
        conf.close()
        ehc = ehcCliMain.ehcCommandLine()
        ehc.main()
    else:
        ehc = ehcCliMain.ehcCommandLine()
        ehc.main()



if __name__ == '__main__':
    main()