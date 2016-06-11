#!/usr/bin/env python
from __future__ import division
import pika
import sys
import json
import os
import subprocess
import boto
import time
from boto.s3.key import Key
from boto.sqs.message import Message
from boto.sqs.message import RawMessage
from pprint import pprint
import logging
import logging.handlers
import argparse
import ConfigParser
import string

config = ConfigParser.ConfigParser()
config.read("/etc/piscan/piscan.ini")

#time.sleep(5)

#LOG_FILENAME = config.get("system", "logloc") + "/piqueue.log"
LOG_FILENAME = "/var/log/piqueue.log"
LOG_LEVEL = logging.DEBUG

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
                # Only log if there is a message (not just a new line)
                if message.rstrip() != "":
                        self.logger.log(self.level, message.rstrip())

#sys.stdout = MyLogger(logger, logging.INFO)
#sys.stderr = MyLogger(logger, logging.ERROR)

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

z = "~"

#def SendQueue(message):
#        try:
#            logger.debug("Connecting to CutQ")
#    	    connection1 = pika.BlockingConnection(pika.ConnectionParameters(host='rxwave.com', port=5672, virtual_host='/', credentials=pika.credentials.PlainCredentials('piscan', 'magic4update')))
#	    channel = connection1.channel()
#	    channel.queue_declare(queue='CutQ', durable=True)
#	    channel.basic_publish(exchange='', routing_key='CutQ', body=message, properties=pika.BasicProperties(delivery_mode = 2,))
#            logger.info("send message to CutQ - " + message)
#	    connection1.close()
#        except:
#            logger.error("Unable to send message to CutQ")

def digits(x):
    return int(100*x)/100.0

def callback(ch, method, properties, body):
    logger.debug("*** Message Recevied (" + body +") ***")

    RID,hash,filename,CutLen,freq,SysSite,Group,Channel,SysType,Modulation,PL,CutDT,RSSI,SqNm,o,p,q,r,s,t,u,v,w = body.split("~")
    aa = "0"

    path=config.get("system", "tmpfileloc") + "/" + str(SqNm) + ".wav"
    wavfl = path
    try:
        try:
            fl=open(path,"rb")
            logger.info("WAV Open : " + path )
        except:
            logger.error("Unable to open WAV: " + path)
        fl.seek(28)
        aa = fl.read(4)
        fl.close()
        byteRate = 0
        for ii in range(4):
            byteRate=byteRate + ord(aa[ii])*pow(256,ii)
        fileSize = os.path.getsize(path)  
        ms = ((fileSize - 44) * 1000) / byteRate
        CutLen =  str(digits(ms/1000))
    except:
        logger.error("Unable to determine WAV size")

    message3 = {}
    message3['RID'] = RID
    message3['Hash'] =  hash
    message3['FileName'] = RID + "-" + SqNm + ".mp3"
    message3['Freq'] =  freq
    message3['CutLen'] = CutLen
    message3['SysSite'] = SysSite
    message3['Group'] = Group
    message3['Channel'] = Channel
    message3['SysType'] = SysType
    message3['Modulation'] = Modulation
    message3['PL'] = PL
    message3['TGID'] = PL
    message3['RSSI'] = RSSI
    message3['Modulation'] = Modulation
    message3['CutDT'] = CutDT
    message3['SeqNum'] = SqNm 
    message = json.dumps(message3)

    access_key = config.get("account", "id")
    secret_key = config.get("account", "secret")

    logger.debug("Sending MP3")

    #################################
    # SEE CREDS IN /ETC/BOTO.CFG    #
    s3_connection = boto.connect_s3()
    #################################
 
    bucket = s3_connection.get_bucket("rxwave-landing-zone",validate=False)
    key = bucket.new_key('/' + str(RID) + "-" + str(SqNm) + '.wav')
    try:
        key.set_contents_from_filename(wavfl, reduced_redundancy=True)
        logger.debug("Send MP3 Successful")
    except:
        logger.debug("Unable to set S3 key contents from file: " + wavfl)

    logger.debug("Sending CutQ message")
    cutqstr = message
    logger.debug("SQS: Connecting to queue")
    conn = boto.sqs.connect_to_region(config.get("global", "region"), aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    my_queue = conn.get_queue(config.get("global", "queue"))
    logger.debug("SQS: Connecting to " + config.get("global", "region"))
    m = RawMessage()
    m.set_body(message)
    logger.debug("SQS: Sending message")
    my_queue.write(m)
    logger.debug("SQS: Message Sent")

    #logger.info("Sent: " + pprint(cutqstr))

    try:
        os.remove(wavfl)
        logger.debug("Deleting WAV")
    except:
        logger.error("Unable to delete WAV: " + wavfl)

    ch.basic_ack(delivery_tag = method.delivery_tag)

logger.debug("*****************STARTING PIQUEUE*******************")
channel.queue_declare(queue='LameQ', durable=True)

logger.debug("Starting PiQueue")
channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback, queue='LameQ')
logger.debug("Starting Consumption")
channel.start_consuming()
