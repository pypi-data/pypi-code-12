## DTLog
#
# Copyright (c) 2016, Expressive Analytics, LLC <info@expressiveanalytics.com>.
# All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# @package Deep Thought
# @author Blake Anderson <blake@expressiveanalytics.com>
# @copyright 2016 Expressive Analytics, LLC <info@expressiveanalytics.com>
# @licence http://choosealicense.com/licenses/mit
# @link http://www.expressiveanalytics.com
# @since version 1.0.0

import json
import os.path
import time
import inspect
import re
import sys
from deepthought.utils.DTSettingsConfig import DTSettingsConfig
#from modules.utils import DTSettingsConfig

class DTLog(object):
    error_fp = None
    info_fp = None
    debug_fp = None
    last_backtrace = None
    _colorize = None

    ## emit major failure message
    @classmethod
    def error(cls,msg,*args):
        if cls.error_fp is None:
            cls.error_fp = cls.openOrCreate("error_log")
        fmt_msg = cls.formatMessage(msg,args)
        return cls.write(cls.error_fp,fmt_msg,"error")

    ## emit warnings
    @classmethod
    def warn(cls,msg,*args):
        if cls.info_fp is None:
            cls.info_fp = cls.openOrCreate("info_log")
        fmt_msg = cls.formatMessage(msg,args)
        return cls.write(cls.info_fp,fmt_msg,"warn")

    ## emit useful information
    @classmethod
    def info(cls,msg,*args):
        if cls.info_fp is None:
            cls.info_fp = cls.openOrCreate("info_log")
        fmt_msg = cls.formatMessage(msg,*args)
        return cls.write(cls.info_fp,fmt_msg,"info")

    ## emit success updates
    @classmethod
    def success(cls,msg,*args):
        if cls.info_fp is None:
            cls.info_fp = cls.openOrCreate("info_log")
        fmt_msg = cls.formatMessage(msg,args)
        return cls.write(cls.info_fp,fmt_msg,"success")

    ## only emits messageif debug
    @classmethod
    def debug(cls,msg,*args):
        if cls.debug_fp is None:
            cls.debug_fp = cls.openOrCreate("debug_log")
        fmt_msg = cls.formatMessage(msg,args)
        cls.last_backtrace = inspect.stack()[1]
        return cls.write(cls.debug_fp,fmt_msg,"debug")

    @classmethod
    def formatMessage(cls,msg,*args):
        if not isinstance(msg, basestring):
            return cls.colorize(str(msg),"INFO")
        strings = []
        for a in args:
            strings.append(cls.colorize(json.dumps(a) if not isinstance(a,basestring) else a,"INFO"))
        return msg.format(*strings)

    @classmethod
    def write(cls,fp,msg,code):
        callerframerecord = inspect.stack()[2]
        frame = callerframerecord[0]
        info = inspect.getframeinfo(frame)
        file = os.path.basename(info.filename)
        line = info.lineno
        timestamp = time.strftime("%a %b %d %H:%M:%S%z %Y")
        msg = json.dumps(msg) if not isinstance(msg,basestring) else str(msg)
        ##@todo lock the file
        if cls._colorize is "pml": #get rid of colorize... for now
            msg = re.sub(r"<dt-color color=[^>]*>","",msg)
            msg = re.sub(r"<\/dt-color>","",msg)
            msg = "[%s] %s:%s:%s:%s\n" % (timestamp,file,line,code,msg)
        elif cls.isCLI():
            re.sub(r"<dt-color color=green>",chr(27)+"[42m",msg)
            re.sub(r"<dt-color color=red>",chr(27)+"[41m",msg)
            re.sub(r"<dt-color color=yellow>",chr(27)+"[43m",msg)
            re.sub(r"<dt-color color=blue>",chr(27)+"[44m",msg)
            re.sub(r"<\/dt-color>",chr(27)+"[0m",msg)
            msg = "[%s] %s:%s:%s:%s\n" % (timestamp,file,line,code,msg)
        else:
            re.sub(r"<dt-color color=green>","<span class='bg-success'>",msg)
            re.sub(r"<dt-color color=red>","<span class='bg-danger'>",msg)
            re.sub(r"<dt-color color=yellow>","<span class='bg-warning'>",msg)
            re.sub(r"<dt-color color=blue>","<span class='bg-info'>",msg)
            re.sub(r"<\/dt-color>","</span>",msg)
        try:
            fp.write(msg)
        except Exception:
            sys.stderr.write("DTLog::write():Could not write to log!")
        ##@todo unlock the file
        return msg

    ## openOrCreate
    # @access protected
    # @param string log_type {"info_log","error_log","debug_log"}
    # @return resource the created/opened file
    @classmethod
    def openOrCreate(cls,log_type):
        config = DTSettingsConfig.sharedSettings()
        cls._colorize = config['logs']['colorize'] if config is not None and "logs" in config and "colorize" in config["logs"] else "pml"
        if config is None or "logs" not in config or log_type not in config['logs']:
            fp = sys.stdout
        else:
            logfile = config['logs'][log_type]
            if not os.path.exists(logfile):
                open(logfile, 'a') #touch
                perms = config["logs"]["permissions"] if config is not None and "logs" in config and "permissions" in config["logs"] else "777"
                os.chmod(logfile,int(perms))
            fp = open(logfile, 'a')
        return fp

    @staticmethod
    def colorize(text,status="INFO"):
        out = ""
        status.upper()
        if status=="SUCCESS":
            out = "green"
        elif status=="FAILURE" or status=="ERROR":
            out = "red"
        elif status=="WARN" or status=="WARNING":
            out = "yellow"
        elif status=="NOTE" or status=="INFO":
            out = "blue"
        else:
            raise Exception("Invalid status: "+status)
        return "<dt-color color=%s>%s</dt-color>" % (out,text)

    @staticmethod
    def isCLI():
        return True

    @classmethod
    def lastBacktrace(cls):
        return cls.lastBacktrace
