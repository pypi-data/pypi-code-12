#!/usr/bin/env python
import serial
import subprocess
import time
import pika
import os
import uuid
import datetime
import logging
import logging.handlers
import argparse
import ConfigParser
import sys

config = ConfigParser.ConfigParser()
config.read("/etc/piscan/piscan.ini")

LOG_FILENAME = config.get("system", "logloc") + "/pirec.log"
LOG_LEVEL = logging.DEBUG  # Could be e.g. "DEBUG" or "WARNING"

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=3)
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class MyLogger(object):
        def __init__(self, logger, level):
                """Needs a logger and a logger level."""
                self.logger = logger
                self.level = level

        def write(self, message):
                if message.rstrip() != "":
                        self.logger.log(self.level, message.rstrip())

sys.stdout = MyLogger(logger, logging.INFO)
sys.stderr = MyLogger(logger, logging.ERROR)

logger.debug("******************STARTING PIREC********************")
#logger.info("*** FORCED SYSTEM EXIT ***")
#sys.exit()

port = config.get("system", "serialport") 
baudrate = config.get("system", "baudrate") 

serTimeout = float(.005) 
TGIDold = 0
metadata = ''

try:
    serialFromScanner = serial.Serial(port, baudrate, timeout=serTimeout)
    serialFromScanner.bytesize = serial.EIGHTBITS 
    serialFromScanner.parity = serial.PARITY_NONE 
    serialFromScanner.stopbits = serial.STOPBITS_ONE 
    serialFromScanner.timeout = 1          
    serialFromScanner.xonxoff = False     
    serialFromScanner.dsrdtr = False
except:
    logger.error('*** Failed to open serial port ***', exc_info=True)
serialFromScanner.flushInput()

def getData(test):
    global serBuffer, nextChar, recflag
    global sqlch, parsed
    serBuffer = '' 
    nextChar = ''
    try:
        test = test + '\r\n'
        serialFromScanner.write(test.encode('UTF-8'))
    except:
        logger.error('*** Failed to write data (' + test + ') to serial port ***', exc_info=True)
    time.sleep(.1)

def receiveData():
    if (serialFromScanner.inWaiting() > 0):
        global nextChar, serBuffer
        global sqlch, parsed
        while nextChar != '\r':
            try:
                nextChar = serialFromScanner.read(1).decode('UTF-8')
                serBuffer += nextChar
            except:
                logger.warning('*** read failed ***', exc_info=True)

def setrecflag():
    global recflag, frames, seqnum
    recflag = 0
    seqnum = 1
    frames = []

def parseData(pserBuffer):
    global sqlch, parsed, GLGData, rssi, freq, ft, modu, att, pl, name1, name2, name3
    parsed = pserBuffer.split(",")
    stringtest = parsed[0]
    length = len(parsed) 
    if stringtest == "GLG":
        if (length >= 9):
            try:
                sqlch = parsed[9]
                if (parsed[1] != ""):
                    ft = parsed[1]
                    modu = parsed[2]
                    att = parsed[3]
                    pl = parsed[4]
                    name1 = parsed[5]
                    name2 = parsed[6]
                    name3 = parsed[7]
                    GLGData = parsed 
            except:
                tempstr = '|'.join(parsed)
                logger.warning('*** parse GLG failed  ***' + tempstr, exc_info=True) 
                sqlch = '2'       
    if stringtest == "PWR":
        if (length >= 2):
            try:
                rssi = parsed[1] 
                freq = parsed[2] 
            except:
                tempstr = '|'.join(parsed)
                logger.warning('*** parse PWR failed  ***' + tempstr, exc_info=True) 
                rssi = '0'
                freq = '0000.0000' 

            if (len(rssi) > 0):
                print(rssi + ' - ' + freq)       
                time.sleep(.1)
                serialFromScanner.flushInput()

global sqlch
sqlch = '1'
setrecflag()



#fl = open(config.get("system", "tmpfileloc") + "/seqnum","r")
#fr = fl.read()
#seqnum = int(float(fr))
#fl.close()

#r = redis.Redis(
#    host='rxwave.com',
#    port=6379,
#    password='xNfEScQVbqxGCT4eJRa6dmhW2ZSVvHab5Vr2dWVNFWZwnvKr')
#seqnum = r.incr('seqnum')

seqnum = uuid.uuid4()

wavfn = config.get("system", "tmpfileloc") + "/" + str(seqnum) + ".wav"

while True: 
    time.sleep(.1)
    getData('GLG')
    receiveData()
    parseData(serBuffer)
    if (sqlch == '0'): 
        # Start recording
        if (recflag == 0):
            cmd = ['sox','-r',config.get("system", "bitrate"),'-c','1','-t','alsa',config.get("system", "audiodevice"),'-t','wav', wavfn] 
            popen = subprocess.Popen ( cmd )
            starttime = datetime.datetime.now()
            logger.debug(wavfn)        
            cmd = 'sox -r ' + config.get("system", "bitrate") + ' -c 1 -t alsa ' + config.get("system", "audiodevice") + ' -t wav ' + wavfn 
            logger.debug(cmd)
            logger.debug("*** START recording ***")        
            recflag=1
        getData('PWR')
        receiveData()
        parseData(serBuffer)
    else:
        # Stop recording and save file
        if (recflag == 1): 
            recflag = 0
            stptime = datetime.datetime.now()
            difference = stptime - starttime
            popen.kill()
            try:
                a = config.get("account", "RID")
                b = config.get("account", "hash")
                c = str(seqnum) + ".wav"
                dd = "{0:.2f}".format(difference.microseconds)
                d = str(difference.seconds) + '.' + str(dd)
                d = str(difference.seconds) + '.' + str(difference.microseconds)
                ee = float(freq)/10000
                e = "{0:.4f}".format(ee)         # Freq 0000.0000
                f = name1        # SysSite   || SysSite
                g = name2        # Sys Group || GroupName
                h = name3        # Talk Grp  || ChannelName
                i = "TRNK"        # CallSign  || SysType
                k = ft           # PL
                if (str(ft.find(".")) != "-1"):
                   i = "CONV"        # CallSign  || SysType
                   k = pl           # TalkGroupID

                j = modu         # Modulation
                l = starttime.strftime("%Y-%m-%d %H:%M:%S")  # CutTime StrTime  YYYY-MM-DD HH:MM:SS
                m = rssi         # RSSI from Pidl.py
                n = str(seqnum)  # Internal counter from seq file

                message = a + "~" + b + "~" + c + "~" + d + "~" + e + "~" + f + "~" + g + "~" + h + "~" + i + "~" + j + "~" + k + "~" + l + "~" + m + "~" + n + "~~~~~~~~~"
                print (message)
                logger.debug("Message creation successgful : " + message )
            except:
                a = a
                logger.warning("*** Message creation unsuccessgful "  )


            try:
                connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
                channel = connection.channel()
                channel.queue_declare(queue='LameQ', durable=True)
                channel.basic_publish(exchange='', routing_key='LameQ', body=message, properties=pika.BasicProperties(delivery_mode = 2,))
                connection.close()
                logger.debug("Message queued to LameQ : " + message )
            except:
                a = a
                logger.warning("*** Message skipped - connect/publish to queue" )

            #seqnum = r.incr('seqnum')
            seqnum = uuid.uuid4()
            #seqnum = seqnum + 1 
            ft = ""

            #fl = open(config.get("system", "tmpfileloc") + "/seqnum","w")
            #fl.write(str(seqnum))
            wavfn = config.get("system", "tmpfileloc") + "/" + str(seqnum) + ".wav"
            #fl.close()





