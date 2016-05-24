#! /usr/bin/python

import logging
import logging.handlers
import time
import os
import pwd
import re
import sys
import urllib2
import platform

import os.path

from optparse import OptionParser

import mistune

from jeju.executor.shell import *
from jeju.executor.editor import *
from jeju.executor.expect import *
from jeju.executor.python import *
from jeju.executor.yaml import *
 
N_LOOKAHEAD = 2
LOOKAHEAD = None
options = None
KV = {}
CUSTOM_KV = {} 
temp_key = None
is_kv = False

__version__ = "0.3.2"

welcome = """

     ___  _______      ___  __   __ 
    |   ||       |    |   ||  | |  |
    |   ||    ___|    |   ||  | |  |
    |   ||   |___     |   ||  |_|  |
 ___|   ||    ___| ___|   ||       |
|       ||   |___ |       ||       |
|_______||_______||_______||_______|

https://github.com/pyengine/jeju

Copyright(c) 2016 Choonho Son.
All rights reserved.

Version: %s

""" % __version__

usage = "usage: %prog [options] arg"

# set up logging to file - see previous section for more details
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='/var/log/jeju.log',
                    filemode='a')

# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)

def clear():
    os.system('clear')

########################
# call executor
# Update Plugin
########################
executor = {
'bash'  : shell_bash,
'c'     : editor_text,
'expect'  : shell_expect,
'text'  : editor_text,
'ini'   : editor_ini,
'python'  : execute_python,
'yaml'  : execute_yaml,
}

"""
Update Table of Index
"""
idx = (0,0,0)
def toi(level):
    global idx
    (x,y,z) = idx
    if level == 1:
        # update x
        x = x + 1
        # clear y,z
        y = 0
        z = 0
        idx = (x,y,z)
        return "%s." % x

    elif level == 2:
        # update y
        y = y + 1
        # clear z
        z = 0
        idx = (x,y,z)
        return "%s-%s." % (x,y)

    elif level == 3:
        # update z
        z = z + 1
        idx = (x,y,z)
        return "%s-%s-%s." % (x,y,z)

################################
# Change user
# TODO: check permission error
################################
def change_user(user_name):
    pw_record = pwd.getpwnam(user_name)
    os.putenv('USER',user_name)
    os.putenv('HOME',pw_record.pw_dir)
    os.setgid(pw_record.pw_gid)
    os.setegid(pw_record.pw_gid)
    os.setuid(pw_record.pw_uid)
    os.seteuid(pw_record.pw_uid)

#################################
# Change working directory
# TODO: check permission error
#################################
def change_dir(new_dir):
    os.chdir(new_dir)


class JunRenderer(mistune.Renderer):
    def __init__(self, **kwargs):
        mistune.Renderer.__init__(self, **kwargs)

    def block_code(self, code, lang):
        #######################
        # Interactive mode
        #######################
        if options.interactive:
            print code
            yn = raw_input("execute next? (Yes/No/Skip)")
            if yn.lower() == 'n' or yn.lower() == 'no':
                sys.exit()
            elif yn.lower() == 's' or yn.lower() == 'skip':
                return "Skipped"

        #################################
        # lookahead : hint for file name 
        # kv : replaceable dictionary
        #################################
        output = executor[lang](code=code, lookahead=LOOKAHEAD, kv=KV)
        # output is dictionary
        # {'input':input_code, 'output': output_code, 'error':error_if_exist}

        if type(output) != dict:
            # This is error of pre-processing
            logging.error(output)
            return '<pre><code class="lang-bash">%s</code></pre>\n' % (lang, output)

        result = ""
        if output.has_key('input') and (output['input'] != None and output['input'] != ''):
            added = output['input']
            added = added.rstrip('\n')
            if not lang:
                added = mistune.escape(added, smart_amp=False)
                return '<pre><code>%s\n</code></pre>\n' % added
            added = mistune.escape(added, quote=True, smart_amp=False)
            result = result + '<b>Input:</b></br>'
            result = result + '<pre><code class="lang-%s">%s\n</code></pre>\n' % (lang, added)

        if output.has_key('output') and (output['output'] != None and output['output'] != ''):
            logging.debug(output['output'])
            added = output['output']
            added = added.rstrip('\n')
            if not lang:
                added = mistune.escape(added, smart_amp=False)
                return '<pre><code>%s\n</code></pre>\n' % added
            added = mistune.escape(added, quote=True, smart_amp=False)
            result = result + "<b>Output:</b></br>"
            result = result + '<pre><code class="lang-%s">%s\n</code></pre>\n' % (lang, added)

        if output.has_key('error') and (output['error'] != None and output['error'] != ''):
            logging.error(output['error'])
            added = output['error']
            added = added.rstrip('\n')
            if not lang:
                added = mistune.escape(added, smart_amp=False)
                return '<pre><code>%s\n</code></pre>\n' % added
            added = mistune.escape(added, quote=True, smart_amp=False)
            result = result + "<b>Error:</b></br>"
            result = result + '<pre><code class="lang-%s">%s\n</code></pre>\n' % (lang, added)
        return result

    def header(self, text, level, raw=None):
        """Rendering header/heading tags like ``<h1>`` ``<h2>``.

        :param text: rendered text content for the header.
        :param level: a number for the header level, for example: 1.
        :param raw: raw text content of the header.
        """
        logging.debug("%s %s" % (toi(level), text))
        time.sleep(1)
        return '<h%d>%s</h%d>\n' % (level, text, level)

class Jeju(mistune.Markdown):
    def pop(self):
        global LOOKAHEAD
        if len(self.tokens) <= 0:
            return None
        if len(self.tokens) >= N_LOOKAHEAD:
            # get reverse index
            r_idx = 0 - N_LOOKAHEAD
            if self.tokens[r_idx]['type'] == 'code':
                LOOKAHEAD = self.tokens[-1]

        self.token = self.tokens.pop()
        return self.token

    def output(self, text, rules=None):
        self.tokens = self.block(text, rules)
        self.tokens.reverse()

        self.inline.setup(self.block.def_links, self.block.def_footnotes)

        out = self.renderer.placeholder()
        while self.pop():
            out += self.tok()
        return out

    def tok(self):
        t = self.token['type']

        # sepcial cases
        if t.endswith('_start'):
            t = t[:-6]
        
        return getattr(self, 'output_%s' % t)()

    def output_table(self):
        aligns = self.token['align']
        aligns_length = len(aligns)
        cell = self.renderer.placeholder()

        global temp_key
        global is_kv
        is_kv = False

        # header part
        header = self.renderer.placeholder()
        for i, value in enumerate(self.token['header']):
            if i == 0:
                if value.lower() == 'keyword':
                    # This is keyword
                    is_kv = True
                else:
                    is_kv = False

            if i == 1 and is_kv == True:
                if value.lower() == 'value':
                    is_kv = True
                else:
                    is_kv = False


            align = aligns[i] if i < aligns_length else None
            flags = {'header': True, 'align': align}
            cell += self.renderer.table_cell(self.inline(value), **flags)

        header += self.renderer.table_row(cell)

        # body part
        body = self.renderer.placeholder()
        for i, row in enumerate(self.token['cells']):
            cell = self.renderer.placeholder()
            for j, value in enumerate(row):
                if is_kv == True:
                    if j == 0:
                        temp_key = value
                    elif j == 1:
                        # if CUSTOM_KV has temp_key,
                        # key is overrided by user.
                        # do not update Key/Value
                        if CUSTOM_KV.has_key(temp_key) == True:
                            logging.info("%s = %s is overrided by user (%s = %s)" % (temp_key, value, temp_key, CUSTOM_KV[temp_key]))
                        else: 
                            KV[temp_key] = value
                            logging.info("Update K[%s] = %s" % (temp_key, value))
                        ######################################
                        # Special case
                        #
                        # USER : change current user
                        # PWD : chnage working directory
                        #######################################
                        if temp_key == "USER":
                            logging.info("Change current user %s -> %s" % (os.environ['USER'], value))
                            change_user(value)

                        if temp_key == "PWD":
                            logging.info("Change working directory %s -> %s" % (os.environ['PWD'], value))
                            change_dir(value)

                        temp_key = None

                align = aligns[j] if j < aligns_length else None
                flags = {'header': False, 'align': align}
                cell += self.renderer.table_cell(self.inline(value), **flags)
            body += self.renderer.table_row(cell)

        return self.renderer.table(header, body)

##########################
# Open markdown documents
#
# support format:
#  full path   : ex) /home/jeju/install.md
# relative path: ex) install.md
# url          : ex) https://github.com/example/install.md
#
# return : contents of url
###########################
def open_doc(f):
    item = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',f)
    if (len(item) == 1):
        # http[s] like
        # open url
        fp = urllib2.urlopen(f)    
        output = fp.read()

    elif (len(item) == 0):
        # local path
        try:
            fp = open(f)
            output = fp.read()
            fp.close()
        except:
            logging.info("Guide book does not exist in local disk")
            guess = "%s/%s" % (options.repo, f)
            logging.info("Find repository: %s" % guess)
            try: 
                ret = urllib2.urlopen(guess)
                if ret.code == 200:
                    output = ret.read()
            except:
                # find OS dependent repository
                distro = detect_dist()
                os = distro['distname'].split(' ')[0].lower()
                guess = "%s/%s/%s" % (options.repo, os, f)
                
                logging.info("Find repository: %s" % guess)
                try:
                    ret = urllib2.urlopen(guess)
                    if ret.code == 200:
                        output = ret.read()
                except:
                    ver2 = distro['ver'].split('.')
                    guess = "%s/%s/%s.%s/%s" % (options.repo, os, ver2[0], ver2[1], f)
                    logging.info("Find repository: %s" % guess)
                    try:
                        ret = urllib2.urlopen(guess)
                        output = ret.read()
                    except:
                        return "# Guide book does not exist! "
    return output


# Detect OS & Version
# return ("distname": "CentOS Linux", "ver":"7.2.1511", "id":"Core")
def detect_dist():    
    (a,b,c) = platform.linux_distribution()
    result = {"distname":a,
            "ver":b,
            "id":c}
    return result



text = """
# Hello World

This is hello world example.
Jeju will read this document, then execute this based on code.

# How to program with C

## create source code

Jeju will create hello.c file in current working directory.

edit hello.c
~~~c
// comment
#include <stdio.h>

int main()
{
    printf("Hello World\\n");
    return 0;
}
~~~

# Compile

Jeju will compile above created file, hello.c

~~~bash
gcc -o hello hello.c
./hello
~~~

"""

####################
# parse custom k/v
#
# param: k1=v1,k2=v2 ...
####################
def parse_kv(param):
    global CUSTOM_KV
    global KV

    items = param.split(",")
    v = ""
    for item in items:
        kv = item.split("=")
        if len(kv) == 1:
            # This is value with comma(,)
            # append previous k=v,new_value
            v = '%s,%s' % (v,kv[0])
        else:
            (k,v) = kv
            
        CUSTOM_KV[k] = v
        KV[k] = v

def main():
    global options
    parser = OptionParser()
    parser.add_option("-m","--markdown", dest="md", \
                    help="Specification documents based on Markdown style",metavar="md file")

    parser.add_option("-l","--logging", dest="logging", \
                    help="Logging level (CRITICAL | ERROR | WARNING | INFO | DEBUG), \
                    default=DEBUG",metavar="logging level", default="DEBUG")

    parser.add_option("-V","--verbose", dest="verbose", \
                    help="Verbose level (console | file | all), default=all", \
                    metavar="verbose level", default="all")

    parser.add_option("-i","--interactive", dest="interactive", \
                    help="Interactive mode asking for execution", \
                    action="store_true", default=False)

    parser.add_option("-k","--kv", dest="kv", \
                    help="""Additional custom/overriding KEY=VALUEs, seperated by comma(,)
                    ex) -k 'k1=value1,k2=value2'
                    """, \
                    metavar="key=value")

    parser.add_option("-r","--repo", dest="repo", \
                    help="Repository of jeju guide book", \
                    default="https://raw.githubusercontent.com/pyengine/jeju-guide/master")


    parser.add_option("-v","--version", dest="version", \
                    help="Show current version", \
                    action="store_true", default=False)


    (options,args) = parser.parse_args()

    if options.version:
        print __version__
        sys.exit()

    if options.kv:
        parse_kv(options.kv)

    if not options.md:
        print "Default instruction is hello world"
        code = text
    else:
        code = open_doc(options.md)

    jun = JunRenderer()
    markdown = Jeju(renderer=jun)

    ###############################
    # Show Jeju mascoat
    ###############################
    if options.verbose and options.verbose == "file":
        pass
    else:
        clear()
        print welcome
        time.sleep(3)

        # split path to (prefix, file)
    if options.md: 
        (prefix, f) = os.path.split(options.md)
    else:
        f = "test"

    if options.logging == "DEBUG":
        level = logging.DEBUG
    elif options.logging == "INFO":
        level = logging.INFO
    elif options.logging == "WARNING":
        level = logging.WARNING
    elif options.logging == "ERROR":
        level = logging.ERROR
    elif options.logging == "CRITICAL":
        level = logging.CRITICAL
    else:
        level = logging.DEBUG

    console.setLevel(level)

    if options.verbose:
        if options.verbose == "console" or options.verbose == "all":
            # add the handler to the root logging
            logging.getLogger('').addHandler(console)
    else:
        logging.getLogger('').addHandler(console)

    # Load hostname
    import socket
    KV['HOSTNAME'] = socket.gethostname()
    KV['IP'] = socket.gethostbyname(KV['HOSTNAME'])

    if options.md:
        logging.info("Start Jeju: %s" % options.md)
    else:
        logging.info("Start Jeju: test")
    if options.kv:
        logging.info("       -kv: %s" % options.kv)

    logging.info("Update K[%s] = %s" % ('HOSTNAME', KV['HOSTNAME']))
    logging.info("Update K[%s] = %s" % ('IP', KV['IP']))

    output = markdown(code)
    # write to file
    fp = open('./%s.html' % f, 'w')
    fp.write(output)
    fp.close()

if __name__ == "__main__":
    main()
