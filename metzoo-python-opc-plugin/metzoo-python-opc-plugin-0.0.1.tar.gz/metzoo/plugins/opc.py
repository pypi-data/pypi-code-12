# -*- coding: utf-8 -*-

import OpenOPC

from time import gmtime
from calendar import timegm
from datetime import datetime

def opc_init(config):
    try:
        opc = OpenOPC.open_client(config["gateway"])
    except KeyError:
        opc = OpenOPC.client()
    
    try:
        server = config["server_name"]
    except KeyError:
        raise ValueError("'server_name' is empty")
    
    try:
        host = config["host_name"]
    except KeyError:
        host = None
    
    try:
        if host is None:
            opc.connect(server)
        else:
            opc.connect(server, host)
    except OpenOPC.OPCError as e:
        raise RuntimeError("can't connect to host: {}, server: {} ".format(host, server))
    
    return opc

def read(config, logger):
    logger.debug("============================== start ==============================")
    
    if not config.has_key("mapping"):
      raise RuntimeError("'{}' mapping don't exists".format(import_stmt))
    
    mapping= config["mapping"]
    opc= opc_init(config)
    data_list = []
    for (tag, value, quality, timestamp) in opc.read(mapping.keys()):
        try:
            t = timegm(gmtime())
            if config["use_opc_time"]:
                t = timegm(datetime.strptime(timestamp, config["timeformat"]).timetuple())
        except:
            pass
        if quality != "Good":
            value= None
        data_list.append( (t, mapping[tag]["agent"], mapping[tag]["metric"], value) )
    
    opc.close()
    logger.debug("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ end ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    return data_list
