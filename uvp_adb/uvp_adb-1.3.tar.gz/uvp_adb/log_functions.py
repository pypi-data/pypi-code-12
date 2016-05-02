# ===========================================
# log_functions.py
#
# Log functions used to show/write log on display/file
#
# Written by Sajjad Ziyaei amiri  (04/12/2016)
# ===========================================

import time
import platform

def UVP_log (text):
    #print "UVP >> ", text
    log = time.strftime("%d/%m/%Y %H:%M:%S")+" >> UVP >> "+ text
    write_log_to_file (log)
    
def UVP_Warning(text):
    #print "UVP >> **** WARNING **** " + text
    log = time.strftime("%d/%m/%Y %H:%M:%S")+" >> UVP >> **** WARNING **** "+ text
    write_log_to_file (log)
    write_error_to_file (log)

def UVP_error(text):
    #print "UVP >> **** ERROR **** " + text
    log = time.strftime("%d/%m/%Y %H:%M:%S")+" >> UVP >> **** ERROR **** "+ text
    write_log_to_file (log)
    write_error_to_file (log)
    
def write_log_to_file(text):
    if "Windows" in platform.system():
        logpath = "uvp.log"
    elif "Linux" in platform.system():
        logpath = "/var/log/uvp.log"
    f = open(logpath,'a')
    f.write(text+"\n")
    f.close()

def write_error_to_file(text):
    if "Windows" in platform.system() :
		logpath = "uvp-error.log"
    elif "Linux" in platform.system() :
		logpath = "/var/log/uvp-error.log"
    f = open(logpath,'a')
    f.write(text+"\n")
    f.close()
