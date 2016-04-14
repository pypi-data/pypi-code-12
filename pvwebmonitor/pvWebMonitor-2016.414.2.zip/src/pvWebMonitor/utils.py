

'''
pvWebMonitor.utils
'''

# Copyright (c) 2005-2015, UChicago Argonne, LLC.
# See LICENSE file for details.


import datetime
import hashlib
import logging
from lxml import etree
import os
import shutil
import sys
import traceback


def copyToWebServer(local_file, web_site_path):
    '''
    copy local file to web server directory (on a local file system)
    
    This copy routine assumes that it is not necessary to use scp to copy the file.
    '''
    # scpToWebServer(os.path.join(localDir, xslFile), xslFile)
    web_site_path = os.path.abspath(web_site_path)
    local_path = os.path.abspath(os.getcwd())
    if web_site_path == local_path: 
        # same directory, no need to copy
        return
    
    web_site_file = os.path.join(web_site_path, local_file)
    if os.path.exists(web_site_file):
        local_file_mtime = os.path.getmtime(local_file)
        web_site_file_mtime = os.path.getmtime(web_site_file)
        if local_file_mtime <= web_site_file_mtime:
            # not a new file, no need to copy
            return

        local_file_cksum = hashlib.md5(local_file).hexdigest()
        web_site_file_cksum = hashlib.md5(web_site_file).hexdigest()
        if local_file_cksum == web_site_file_cksum:
            # the same file, no need to copy
            return

    shutil.copyfile(local_file, web_site_file)


def getTime():
    '''simple wrapper for common timenow() function'''
    return datetime.datetime.now()


def logMessage(message):
    '''
    log a message or report from pvWebMonitor

    :param str message: words to be logged
    '''
    now = getTime()
    name = os.path.basename(sys.argv[0])
    pid = os.getpid()
    text = "(%d,%s,%s) %s" % (pid, name, now, message)
    logging.info(text)


def logException(troublemaker):
    '''
    write an exception report to the log file

    :param obj troublemaker: instance of Exception
    '''
    msg = "problem with %s:" % troublemaker
    for _ in msg.splitlines():
        logMessage(_)
    for _ in traceback.format_exc().splitlines():
        logMessage('\t' + _)


def validate(xml_tree, xml_schema_file):
    '''
    validate an XML document tree against an XML Schema file

    :param obj xml_tree: instance of etree._ElementTree
    :param str xml_schema_file: name of XML Schema file (local to package directory)
    '''
    path = os.path.abspath(os.path.dirname(__file__))
    xsd_file_name = os.path.join(path, xml_schema_file)
    if not os.path.exists(xsd_file_name):
        raise IOError('Could not find XML Schema file: ' + xml_schema_file)
    
    xsd_doc = etree.parse(xsd_file_name)
    xsd = etree.XMLSchema(xsd_doc)

    return xsd.assertValid(xml_tree)


def writeFile(output_file, contents):
    '''
    write contents to file

    :param str output_file: file to be written (path is optional)
    :param str contents: text to write in *output_file*
    '''
    f = open(output_file, 'w')
    f.write(contents)
    f.close()


def xslt_transformation(xslt_file, src_xml_file, result_xml_file):
    '''
    transform an XML file using an XSLT

    :param str xslt_file: name of XSLT file
    :param str src_xml_file: name of XML file
    :param str result_xml_file: name of output XML file
    '''
    src_doc = etree.parse(src_xml_file)
    xslt_doc = etree.parse(xslt_file)
    transform = etree.XSLT(xslt_doc)
    result_doc = transform(src_doc)
    buf = etree.tostring(result_doc, pretty_print=True)
    writeFile(result_xml_file, buf)
