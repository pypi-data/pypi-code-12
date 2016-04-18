# Copyright: 2011 Steve Challis (http://schallis.com)
# Copyright: 2012 MoinMoin:ReimarBauer
# License: MIT 

"""
    bigbluebutton.utils

    This module contains helper functions to access bigbluebutton servers

"""
import requests
import xml.etree.ElementTree as ET
from hashlib import sha1

def parse(response):
    """
    :param reponse: XML Data 
    """
    try:
        xml = ET.fromstring(response)
        code = xml.find('returncode').text
        if code == 'SUCCESS':
            return xml
        else:
            raise
    except:
        return None

def api_call(salt, query, call):
    """
    builds the hash based on the call, query and salt
    
    :param salt: The security salt defined for your bigbluebutton instance
    :param query: The query parameters for calling the bigbluebutton resource
    :param call: The bigbluebutton resource name
    """
    prepared = "%s%s%s" % (call, query, salt)
    checksum = sha1(prepared).hexdigest()
    return "%s&checksum=%s" % (query, checksum)

def get_xml(bbb_api_url, salt, call, query, pre_upload_slide=None):
    """
    gets XML from the bigbluebutton ressource

    :param bbb_api_url: The url to your bigbluebutton instance (including the api/)
    :param salt: The security salt defined for your bigbluebutton instance
    :param call: The bigbluebutton resource name
    :param query: The query parameters for calling the bigbluebutton resource
    :param pre_upload_slide: on create a file could be uploaded
    """

    hashed = api_call(salt, query, call)
    url = bbb_api_url + call + '?' + hashed
    if call == "create" and pre_upload_slide is not None:
        xml = "<?xml version='1.0' encoding='UTF-8'?> <modules> <module name='presentation'> <document url='%(pre_upload_slide)s'/> </module></modules>" % {"pre_upload_slide": pre_upload_slide}
        headers = {'Content-Type': 'application/xml'}
        return parse(requests.post(url, data=xml, headers=headers).content)
    else:
        return parse(requests.get(url).content)
