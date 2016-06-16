# -*- coding: utf-8 -*-

import time, datetime, re
import glob, os

def parse_time(str_date):
    return int(time.mktime(time.strptime(str_date+'m', '%d/%m/%y %I:%M%p')))

def parse_value(value):
    if (type(value) == str) and (value.strip() == ''):
        return None
    else:
        try:
            return float(value)
        except ValueError:
            return None

def read(config, logger):
    logger.debug("============================== start ==============================")
    
    result  = []
    path    = config["path"].strip() if config.has_key("path") else "."
    filename= config["filename"]
    lines   = config["lines"] if config.has_key("lines") else 1
    mapping = config["mapping"]
    #
    for file in glob.glob(path+"/"+filename):
        try:
            with open(file) as f:
                lines= f.read().split('\n')[-1-lines:-1]
            for line in lines:
                timestamp = parse_time(line[0:15])
                for key in mapping.keys():
                    match= re.match("\[(\d+):(\d+)\]", key)
                    if match:
                        agent  = mapping[key]["agent"]
                        metric = mapping[key]["metric"]
                        value  = parse_value(line[int(match.group(1))-1:int(match.group(2))])
                        result.append( (timestamp, agent, metric, value) )
        except BaseException as e:
            logger.error(e)  
        #
    #
    logger.debug("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ end ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    return result
