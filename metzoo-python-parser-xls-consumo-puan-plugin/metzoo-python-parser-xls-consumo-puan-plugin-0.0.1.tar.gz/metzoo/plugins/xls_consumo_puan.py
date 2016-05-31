# -*- coding: utf-8 -*-

import time, datetime, re
import glob, os
import xlrd

def parse_time(str_date, str_time):
    str_months = {"enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6, "julio": 7, "agosto": 8, "setiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12}
    match_date = re.match("(.+), (\d+) de (\w+) de (\d+)", str_date)
    match_time = re.match("(\d+):(\d+):(\d+) *Hs", str_time)
    result= datetime.datetime(int(match_date.group(4)), str_months[match_date.group(3)], int(match_date.group(2)), int(match_time.group(1)), int(match_time.group(2)), int(match_time.group(3)))
    return time.mktime(result.timetuple())

def parse_value(value):
    if type(value) != float:
        return None
    elif value < 0:
        return None
    else:
        return value

def read(config, logger):
    logger.debug("============================== start ==============================")
    
    result  = []
    path    = config["path"].strip() if config.has_key("path") else "."
    mapping = config["mapping"]
    #filename= config["filename"]
    filename= (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d_Diario.xls').replace('-0','-')
    
    for file in glob.glob(path+"/"+filename):
        try:
            book = xlrd.open_workbook(file)
            for inx in [0,1]:
                sheet= book.sheet_by_index(inx)
                date= sheet.cell_value(rowx=2, colx=1)
                for col in [2,3,4,5]:
                    timestamp= parse_time(date, sheet.cell_value(rowx=5, colx=col))
                    for row in range(6, sheet.nrows):
                        name   = sheet.cell_value(rowx=row, colx=1)
                        if name == "":
                            break
                        
                        if mapping.has_key(name):
                            agent  = mapping[name]["agent"]
                            metric = mapping[name]["metric"]
                            value  = parse_value(sheet.cell_value(rowx=row, colx=col))
                            result.append( (timestamp, agent, metric, value) )
        except:
            logger.error("Plugin error")  
        #
    #
    logger.debug("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ end ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    return result
