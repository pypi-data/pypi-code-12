#!/usr/bin/python

# Copyright (c) 2012 EMC Corporation
# All Rights Reserved
#
# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.

import os
import sys
import requests
import cookielib
import common
import getpass
from common import SOSError
from requests.exceptions import SSLError
from requests.exceptions import ConnectionError
from requests.exceptions import TooManyRedirects
from requests.exceptions import Timeout
import socket
import json
import ConfigParser


class Authentication(object):

    '''
    The class definition for authenticating the specified user
    '''

    # Commonly used URIs for the 'Authentication' module
    URI_SERVICES_BASE = ''
    URI_AUTHENTICATION = '/login'
    URI_VDC_AUTHN_PROFILE = URI_SERVICES_BASE + '/vdc/admin/authnproviders'
    URI_VDC_AUTHN_PROFILES = (URI_SERVICES_BASE +
                              '/vdc/admin/authnproviders/{0}')

    HEADERS = {'Content-Type': 'application/json',
               'ACCEPT': 'application/json', 'X-EMC-REST-CLIENT': 'TRUE'}

    SEARCH_SCOPE = ['ONELEVEL', 'SUBTREE']
    BOOL_VALS = ['true', 'false']
    ZONE_ROLES = ['SYSTEM_ADMIN', 'SECURITY_ADMIN', 'SYSTEM_MONITOR',
                  'SYSTEM_AUDITOR']

    def __init__(self, ipAddr, port):
        '''
        Constructor: takes IP address and port of the ECS instance.
        These are needed to make http requests for REST API
        '''
        self.__ipAddr = ipAddr
        self.__port = port

    #####################################
    #
    #####################################
    def getCookie(self, username, cookiedir, cookiefile=None):
        token = None
        #cookiefile = common.COOKIE

        if sys.platform.startswith('linux'):
            #print("JMC platform seems to be linux")
            parentshellpid = os.getppid()
            if(cookiefile is None):
                if (parentshellpid is not None):
                    cookiefile = str(username) + 'cookie' + str(parentshellpid)
                else:
                    cookiefile = str(username) + 'cookie'
            form_cookiefile = cookiedir + '/' + cookiefile
        elif sys.platform.startswith('win'):
            #print("JMC platform seems to be windows")
            if (cookiefile is None):
                cookiefile = str(username) + 'cookie'
            form_cookiefile = cookiedir + '\\' + cookiefile
        else:
            #print("JMC platform is neither linux nor windows")
            if (cookiefile is None):
                cookiefile = str(username) + 'cookie'
            form_cookiefile = cookiedir + '/' + cookiefile

        if (form_cookiefile):
            #print("JMC were able to create the form_cookiefile string")
            if (not os.path.exists(form_cookiefile)):
                #print("JMC form_cookiefile does NOT exist")
                return None 
                           
            if (not os.path.isfile(form_cookiefile)):
                #print("JMC form_cookiefile does exist but isn't a file")
                return None

            #print("JMC opening the tokenfile")
            tokenfile = open(form_cookiefile)
            token = tokenfile.read()
            tokenfile.close()
            #print("JMC token file has been read and closed")
        return token 

    def authenticate_user(self, username, password, cookiedir, cookiefile):
        '''
        Makes REST API call to generate the cookiefile for the
        specified user after validation.
        Returns:
            SUCCESS OR FAILURE
        '''

        if cookiedir is None:
            print("No cookiedir arg was passed in. Will attempt to use the 'ECS_CLI_INSTALL_DIR' dir from ecscli.profile") 

            cookiedir = common.getenv('ECS_CLI_INSTALL_DIR') 
            if sys.platform.startswith('win'):
                cookiedir = cookiedir + '\\cookie'
            else:
                cookiedir = cookiedir + '/cookie/'



            if (cookiedir is None):
                raise SOSError(SOSError.NOT_FOUND_ERR,
                               "ECS_CLI_INSTALL_DIR is not set." +
                               " Please set this variable in ecscli.profile and source this file or pass in a -cookiedir arg\n")
            else:
                print("The cli will attempt to use the ECS_CLI_INSTALL_DIR: '" + cookiedir + "' to store the cookie file")
        else:
            print("The cookie directory to be used was passed in as an arg with value: " + cookiedir)

        SEC_REDIRECT = 302
        SEC_AUTHTOKEN_HEADER = 'X-SDS-AUTH-TOKEN'
        LB_API_PORT = 4443
        # Port on which load-balancer/reverse-proxy listens to all incoming
        # requests for ECS REST APIs
        APISVC_PORT = 8443  # Port on which apisvc listens to incoming requests

        cookiejar = cookielib.LWPCookieJar()

        url = ('https://' + str(self.__ipAddr) + ':' + str(self.__port) +
               self.URI_AUTHENTICATION)

        try:
            '''
            attempt to add cookie to header if it's not None
            if the auth request is sent without also sending
            the current cookie, then a new token will be returned
            There are only 100 active tokens allowed. So the client
            should send the current token to check it's validitity
            '''
            fd_content = self.getCookie(username, cookiedir, cookiefile)
            if (fd_content != None):
                #print("JMC now setting this tokenfile info as the X-SDS-AUTH-TOKEN header")
                self.HEADERS['X-SDS-AUTH-TOKEN'] = fd_content

            if(self.__port == APISVC_PORT):
                #print("JMC self.__port == APISVC_PORT")
                login_response = requests.get(
                    url, headers=self.HEADERS, verify=False,
                    auth=(username, password), cookies=cookiejar,
                    allow_redirects=False, timeout=common.TIMEOUT_SEC)
                if(login_response.status_code == SEC_REDIRECT):
                    location = login_response.headers['Location']
                    if(not location):
                        raise SOSError(
                            SOSError.HTTP_ERR, "The redirect location of " +
                            "the authentication service is not provided")
                    # Make the second request
                    login_response = requests.get(
                        location, headers=self.HEADERS, verify=False,
                        cookies=cookiejar, allow_redirects=False,
                        timeout=common.TIMEOUT_SEC)
                    if(not (login_response.status_code ==
                            requests.codes['unauthorized'])):
                        raise SOSError(
                            SOSError.HTTP_ERR, "The authentication service" +
                            " failed to reply with 401")

                    # Now provide the credentials
                    login_response = requests.get(
                        location, headers=self.HEADERS,
                        auth=(username, password), verify=False,
                        cookies=cookiejar, allow_redirects=False,
                        timeout=common.TIMEOUT_SEC)
                    if(not login_response.status_code == SEC_REDIRECT):
                        raise SOSError(
                            SOSError.HTTP_ERR,
                            "Access forbidden: Authentication required")
                    location = login_response.headers['Location']
                    if(not location):
                        raise SOSError(
                            SOSError.HTTP_ERR, "The authentication service" +
                            " failed to provide the location of the service" +
                            " URI when redirecting back")
                    authToken = login_response.headers[SEC_AUTHTOKEN_HEADER]
                    if (not authToken):
                        details_str = self.extract_error_detail(login_response)
                        raise SOSError(SOSError.HTTP_ERR,
                                       "The token is not generated" +
                                       " by authentication service." + details_str)
                    # Make the final call to get the page with the token
                    newHeaders = self.HEADERS
                    newHeaders[SEC_AUTHTOKEN_HEADER] = authToken
                    login_response = requests.get(
                        location, headers=newHeaders, verify=False,
                        cookies=cookiejar, allow_redirects=False,
                        timeout=common.TIMEOUT_SEC)
                    if(login_response.status_code != requests.codes['ok']):
                        raise SOSError(
                            SOSError.HTTP_ERR, "Login failure code: " +
                            str(login_response.status_code) + " Error: " +
                            login_response.text)
            elif(self.__port == LB_API_PORT):
                #print("JMC self.__port == LB_API_PORT")
                ###############################################
                #print the headers dictionary key and value pairs
                '''
                print("++++++++start headers++++++++++++")
                for key, value in self.HEADERS.iteritems():
                   print("JMC auth: " + key + ": " + str(value))
                print("---------end headers-------------")
                '''
                #################################################


                login_response = requests.get(
                    url, headers=self.HEADERS, verify=False,
                    cookies=cookiejar, allow_redirects=False)


                ###############################################
                '''
                print("JMC login_response: " + str(login_response))
                tmp = requests.codes['unauthorized']
                print("JMC an unauthorized response would be: " + str(tmp))
                '''
                ###############################################

  
                ###############################################
                '''
                print("++++++++start response headers++++++++++")
                for k,v in login_response.headers.iteritems():
                    print("JMC response header: " + k + ": " + str(v))
                print("--------end response headers------------")
                '''
                ###############################################

                if(login_response.status_code == requests.codes['unauthorized']):
                    #print("JMC this is the unauthorized response. TRY TO RESEND with auth username/password")
                    # Now provide the credentials
                    login_response = requests.get(
                        url, headers=self.HEADERS, auth=(username, password),
                        verify=False, cookies=cookiejar, allow_redirects=False)

                    ##################################################################
                    #JMC fix to the issue of ECS not recognizing a token sent in the header
                    if(SEC_AUTHTOKEN_HEADER not in login_response.headers):
                        try:
                            self.HEADERS.pop('X-SDS-AUTH-TOKEN')
                            login_response = requests.get(
                                url, headers=self.HEADERS, auth=(username, password),
                                verify=False, cookies=cookiejar, allow_redirects=False)
                        except KeyError:
                            pass
                    ##########################################################

                else:
                    print("status code was NOT UNauthorized... ie you are still authorized when using previous cookie")
                    print("login_response.status_code = " + str(login_response.status_code))
                    ##########################HERE IS THE YOU ARE STILL AUTH'd RETURN
                    return "authorization confirmed"

                authToken = None
                if(SEC_AUTHTOKEN_HEADER in login_response.headers):
                    #print("JMC the auth token is in the SEC_AUTHTOKEN_HEADER response header")
                    authToken = login_response.headers[SEC_AUTHTOKEN_HEADER]
                    '''
                    if (authToken is not None):
                        print("JMC authToken: " + authToken)
                    else:
                        print("JMC authToken is None")
                    '''
                else:
                    #JMC
                    #if the first request.get auth worked when doing a re-auth, then you get here
                    #normally. However if you get here from the second retry requests.get,
                    #there's a problem

                    #print("no need to update the authToken. There is no SEC_AUTHTOKEN_HEADER")
                    print("current token appears to be valid")
                    print("login_response.status_code: " + str(login_response.status_code))

            else:
                raise SOSError(
                    SOSError.HTTP_ERR,
                    "Incorrect port number.  Load balanced port is: " +
                    str(LB_API_PORT) + ", api service port is: " +
                    str(APISVC_PORT) + ".")

            if (not authToken):
                #print("JMC not sure we should've gotten here if you were preauthorized")
                details_str = self.extract_error_detail(login_response)
                raise SOSError(
                    SOSError.HTTP_ERR,
                    "The token is not generated by authentication service."+details_str)

            if (login_response.status_code != requests.codes['ok']):
                #print("JMC login_response.status_code != requests.codes['ok']")
                error_msg = None
                if(login_response.status_code == 401):
                    error_msg = "Access forbidden: Authentication required"
                elif(login_response.status_code == 403):
                    error_msg = ("Access forbidden: You don't have" +
                                 " sufficient privileges to perform" +
                                 " this operation")
                elif(login_response.status_code == 500):
                    error_msg = "Bourne internal server error"
                elif(login_response.status_code == 404):
                    error_msg = "Requested resource is currently unavailable"
                elif(login_response.status_code == 405):
                    error_msg = ("GET method is not supported by resource: " +
                                 url)
                elif(login_response.status_code == 503):
                    error_msg = ("Service temporarily unavailable:" +
                                 " The server is temporarily unable" +
                                 " to service your request")
                else:
                    error_msg = login_response.text
                    if isinstance(error_msg, unicode):
                        error_msg = error_msg.encode('utf-8')
                raise SOSError(SOSError.HTTP_ERR, "HTTP code: " +
                               str(login_response.status_code) +
                               ", response: " + str(login_response.reason) +
                               " [" + str(error_msg) + "]")

        except (SSLError, socket.error, ConnectionError, Timeout) as e:
            raise SOSError(SOSError.HTTP_ERR, str(e))

        #print("JMC response was handled now do something. I'm not sure any of this should be done if already authd")
        form_cookiefile = None
        parentshellpid = None
        installdir_cookie = None
        if sys.platform.startswith('linux'):
            parentshellpid = os.getppid()
            if(cookiefile is None):
                if (parentshellpid is not None):
                    cookiefile = str(username) + 'cookie' + str(parentshellpid)
                else:
                    cookiefile = str(username) + 'cookie'
            form_cookiefile = cookiedir + '/' + cookiefile
            if (parentshellpid is not None):
                installdir_cookie = '/cookie/' + str(parentshellpid)
            else:
                installdir_cookie = '/cookie/cookiefile'
        elif sys.platform.startswith('win'):
            if (cookiefile is None):
                cookiefile = str(username) + 'cookie'
            form_cookiefile = cookiedir + '\\' + cookiefile
            installdir_cookie = '\\cookie\\cookiefile'
        else:
            if (cookiefile is None):
                cookiefile = str(username) + 'cookie'
            form_cookiefile = cookiedir + '/' + cookiefile
            installdir_cookie = '/cookie/cookiefile'
        
        try:
            if(common.create_file(form_cookiefile)):
                tokenFile = open(form_cookiefile, "w")
                if(tokenFile):
                    tokenFile.write(authToken)
                    tokenFile.close()

                    ret_val = username + ' : Authenticated Successfully\n' + form_cookiefile + ' : Cookie saved successfully'
                    return ret_val
                else:
                    raise SOSError(SOSError.NOT_FOUND_ERR,
                                   " Failed to save the cookie file path "
                                   + form_cookiefile)

        except (OSError) as e:
            raise SOSError(e.errno, cookiedir + " " + e.strerror)
        except IOError as e:
            raise SOSError(e.errno, e.strerror)

        #shouldn't get here unless there was a problem
        return "There was a problem authenticating"


    def extract_error_detail(self, login_response):
        details_str = ""
        try:
            if(login_response.content):
                json_object = common.json_decode(login_response.content)
                if(json_object.has_key('details')):
                    details_str = json_object['details']

            return details_str
        except SOSError as e:
            return details_str


    def add_authentication_provider(self, mode, url, certificate, managerdn,
                                    managerpwd, searchbase, searchfilter,
                                    searchkey, groupattr, name, domains,
                                    whitelist, searchscope, description,
                                    disable, validatecertificate, maxpagesize, validate_certificates):
        '''
        Makes REST API call to add authentication provider
        specified user after validation.
        Returns:
            SUCCESS OR FAILURE
        '''

        domainlist_array = []
        domainlist_array = domains.split(',')

        urlslist_array = []
        urlslist_array = url.split(',')

        parms = {'mode': mode,                
                 'server_urls': urlslist_array,
                 #'server_cert': certificate,
                 'manager_dn': managerdn,       
                 'manager_password': managerpwd,
                 'search_base': searchbase,    
                 'search_filter': searchfilter,
                 'search_scope': searchscope, 
                 'group_attribute': groupattr,
                 'name': name,               
                 'description': description, 
                 'disable': disable,         
                 'max_page_size': maxpagesize,
                 'validate_certificates': validate_certificates,
                 'domains': domainlist_array}  

        if(whitelist is not ""):
            whitelist_array = []
            whitelist_array = whitelist.split(',')
            parms['group_whitelist_values'] = whitelist_array


        body = json.dumps(parms)

        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port, "POST",
            Authentication.URI_VDC_AUTHN_PROFILE,
            body)

    def list_authentication_provider(self):
        '''
        Makes REST API call to list authentication providers
        Returns:
            SUCCESS OR FAILURE
        '''
        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port, "GET",
            Authentication.URI_VDC_AUTHN_PROFILE,
            None)

        o = common.json_decode(s)

        profiles = []
        for pr in o['authnprovider']:
            profiles.append(pr)

        return profiles

    def query_authentication_provider(self, name):
        '''
        Makes REST API call to query authentication providers
        Returns:
            SUCCESS OR FAILURE
        '''
        profiles = self.list_authentication_provider()

        for pr in profiles:

            profile = self.show_authentication_provider_by_uri(pr['id'])
            if (profile['name'] == name):
                return profile['id']

    def show_authentication_provider(self, name, xml=False):
        '''
        Makes REST API call to show authentication providers
        Returns:
            SUCCESS OR FAILURE
        '''
        profiles = self.list_authentication_provider()

        for pr in profiles:
            profile = self.show_authentication_provider_by_uri(pr['id'], False)

            if ((profile) and (profile['name'] == name)):
                if(xml):
                    profile = self.show_authentication_provider_by_uri(
                    pr['id'], True)
		    dictobj = json.loads(profile)
		    dictobj_final = dict()
		    dictobj_final['authnprovider'] = dictobj
	            
		    res = common.dict2xml(dictobj_final)
		    return res.display()
                return profile

        raise SOSError(SOSError.NOT_FOUND_ERR,
                       "Authentication Provider with name '" +
                       name + "' not found")

    def delete_authentication_provider(self, name):
        '''
        Makes REST API call to delete authentication provider
        Returns:
            SUCCESS OR FAILURE
        '''
        uri = self.query_authentication_provider(name)

        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port, "DELETE",
            Authentication.URI_VDC_AUTHN_PROFILES.format(uri), None)

        return str(s) + " ++ " + str(h)

    def show_authentication_provider_by_uri(self, uri, xml=False):
        '''
        Makes REST API call to show  authentication provider by uri
        Returns:
            SUCCESS OR FAILURE
        '''

        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port, "GET",
            Authentication.URI_VDC_AUTHN_PROFILES.format(uri),
            None)

        if(not xml):
            o = common.json_decode(s)
            if('inactive' in o):
                if(o['inactive']):
                    return None
            return o
        else:
            return s

    def cleanup_dict(self, lst):

        if(len(lst['add']) == 0):
            del lst['add']

        if(len(lst['remove']) == 0):
            del lst['remove']

        return lst

    def update_authentication_provider(self, mode, add_urls, remove_urls,
                                       certificate, managerdn, managerpwd,
                                       searchbase, searchfilter, searchkey,
                                       groupattr, name, add_domains,
                                       remove_domains, add_whitelist,
                                       remove_whitelist, searchscope,
                                       description, disable,
                                       validatecertificate, maxpagesize):
        '''
        Makes REST API call to generate the cookiefile for the
        specified user after validation.
        Returns:
            SUCCESS OR FAILURE
        '''

        authnprov_id = self.query_authentication_provider(name)

        server_assignments = dict()
        domain_assignments = dict()
        whitelist_assignments = dict()

        urls = dict()
        domains = dict()
        whitelist = dict()

        urls['add'] = []
        for iter in add_urls:
            if(iter is not ""):
                urls['add'].append(iter)

        urls['remove'] = []
        for iter in remove_urls:
            if(iter is not ""):
                urls['remove'].append(iter)

        domains['add'] = []
        for iter in add_domains:
            if(iter is not ""):
                domains['add'].append(iter)

        domains['remove'] = []
        for iter in remove_domains:
            if(iter is not ""):
                domains['remove'].append(iter)

        whitelist['remove'] = []
        for iter in remove_whitelist:
            if(iter is not ""):
                whitelist['remove'].append(iter)

        whitelist['add'] = []
        for iter in add_whitelist:
            if(iter is not ""):
                whitelist['add'].append(iter)

        '''for domain in add_domains:
                domainlist.append({'domain': domain})
            domains['add'] = domainlist #add_domains'''

        parms = {'mode': mode,
                 'manager_dn': managerdn,
                 'manager_password': managerpwd,
                 'search_base': searchbase,
                 'search_filter': searchfilter,
                 'search_scope': searchscope,
                 'group_attribute': groupattr,
                 'name': name,
                 'description': description,
                 'disable': disable,
                 'max_page_size': maxpagesize}

        if((len(urls['add']) > 0) or (len(urls['remove']) > 0)):
            urls = self.cleanup_dict(urls)
            parms['server_url_changes'] = urls

        if((len(domains['remove']) > 0) or (len(domains['add']) > 0)):
            domains = self.cleanup_dict(domains)
            parms['domain_changes'] = domains

        if((len(whitelist['add']) > 0) or (len(whitelist['remove']) > 0)):
            whitelist = self.cleanup_dict(whitelist)
            parms['group_whitelist_value_changes'] = whitelist

        body = json.dumps(parms)

        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port, "PUT",
            Authentication.URI_VDC_AUTHN_PROFILES.format(authnprov_id),
            body)

def add_authentication_provider(args):
    obj = Authentication(args.ip, args.port)
    try:
        # read authentication provider  parameters from configuration file
        config = ConfigParser.RawConfigParser()
        inif = open(args.configfile, 'rb')
        config.readfp(inif)
        sectionslst = config.sections()

        if(len(sectionslst) == 0):
            raise SOSError(
                SOSError.NOT_FOUND_ERR,
                "Authentication Provider configuration file is empty")

        for sectioniter in sectionslst:
            mode = config.get(sectioniter, "mode")
            url = config.get(sectioniter, "url")
            managerdn = config.get(sectioniter, 'managerdn')
            searchbase = config.get(sectioniter, 'searchbase')
            searchfilter = config.get(sectioniter, 'searchfilter')
            #searchkey = config.get(sectioniter, 'searchkey')
            groupattr = config.get(sectioniter, 'groupattr')
            name = config.get(sectioniter, 'name')
            domains = config.get(sectioniter, 'domains')
            whitelist = config.get(sectioniter, 'whitelist')
            description = config.get(sectioniter, 'description')
            searchscope = config.get(sectioniter, 'searchscope')

            maxpagesize = config.get(sectioniter, 'maxpagesize')
            disable = config.get(sectioniter, 'disable')
            validate_certificates = config.get(sectioniter, 'validate_certificates')

            if((domains is "") or (url is "") or (managerdn is "") or 
               (searchbase is "") or (searchfilter is "")
               or (groupattr is "") or (name is "") or (description is "") or
               (searchscope is "") or (mode is "") or (validate_certificates is "")):
                raise SOSError(SOSError.VALUE_ERR, "domains," +
                               "url,managerdn," +
                               "searchbase,searchfilter,groupattr," +
                               "name,description,searchscope, validate_certificates and mode" +
                               " can not be empty")

            defined_and_valid_value('search scope', searchscope,
                                    Authentication.SEARCH_SCOPE)
            defined_and_valid_value('disable', disable,
                                    Authentication.BOOL_VALS)
            defined_and_valid_value('validate_certificates', validate_certificates,
                                    Authentication.BOOL_VALS)

            passwd_user = common.get_password(name)

            res = obj.add_authentication_provider(
                mode, url, None, managerdn, passwd_user, searchbase,
                searchfilter, None, groupattr, name, domains, whitelist,
                searchscope, description, disable, None,
                maxpagesize, validate_certificates)

    except IOError as e:
        common.format_err_msg_and_raise("add", "authentication provider",
                                        e[1], e.errno)

    except SOSError as e:
        common.format_err_msg_and_raise("add", "authentication provider",
                                        e.err_text, e.err_code)

    except ConfigParser.NoOptionError as e:
        common.format_err_msg_and_raise("add", "authentication provider",
                                        str(e), SOSError.NOT_FOUND_ERR)

    except (ConfigParser.ParsingError, ConfigParser.Error) as e:
        common.format_err_msg_and_raise("add", "authentication provider",
                                        str(e), SOSError.VALUE_ERR)


def delete_authentication_provider(args):
    obj = Authentication(args.ip, args.port)
    try:
        res = obj.delete_authentication_provider(args.name)
    except SOSError as e:
        common.format_err_msg_and_raise("delete", "Authentication Provider",
                                        e.err_text, e.err_code)


def show_authentication_provider(args):
    obj = Authentication(args.ip, args.port)
    try:
        res = obj.show_authentication_provider(args.name, args.xml)
        if(args.xml):
            return res
        return common.format_json_object(res)
    except SOSError as e:
        common.format_err_msg_and_raise("show", "Authentication Provider",
                                        e.err_text, e.err_code)


def get_attribute_value(config, sectioniter, attrname):
    try:
        val = config.get(sectioniter, attrname)
        if(val is ''):
            return None
        else:
            return val

    except IOError as e:
        raise e

    except SOSError as e:
        raise e

    except ConfigParser.NoOptionError as e:
        raise e

    except (ConfigParser.ParsingError, ConfigParser.Error) as e:
        raise e


def update_authentication_provider(args):
    obj = Authentication(args.ip, args.port)
    try:
        # read authentication provider  parameters from configuration file
        config = ConfigParser.RawConfigParser()
        inif = open(args.configfile, 'rb')
        config.readfp(inif)
        sectionslst = config.sections()

        if(len(sectionslst) == 0):
            raise SOSError(
                SOSError.NOT_FOUND_ERR,
                "Authentication Provider configuration file is empty")

        for sectioniter in sectionslst:
            mode = get_attribute_value(config, sectioniter, "mode")

            add_urls = config.get(sectioniter, "add-urls")
            remove_urls = config.get(sectioniter, "remove-urls")
            add_domains = config.get(sectioniter, 'add-domains')
            remove_domains = config.get(sectioniter, 'remove-domains')
            add_whitelist = config.get(sectioniter, 'add-whitelist')
            remove_whitelist = config.get(sectioniter, 'remove-whitelist')

            managerdn = get_attribute_value(config, sectioniter, 'managerdn')
            searchbase = get_attribute_value(config, sectioniter, 'searchbase')
            searchfilter = get_attribute_value(config, sectioniter,
                                               'searchfilter')
            #searchkey = config.get(sectioniter, 'searchkey')
            groupattr = get_attribute_value(config, sectioniter, 'groupattr')
            name = get_attribute_value(config, sectioniter, 'name')
            description = get_attribute_value(config, sectioniter,
                                              'description')
            searchscope = get_attribute_value(config, sectioniter,
                                              'searchscope')

            maxpagesize = get_attribute_value(config, sectioniter,
                                              'maxpagesize')
            disable = get_attribute_value(config, sectioniter, 'disable')

            defined_and_valid_value('search scope', searchscope,
                                    Authentication.SEARCH_SCOPE)
            defined_and_valid_value('disable', disable,
                                    Authentication.BOOL_VALS)

            passwd_user = common.get_password(name)

            res = obj.update_authentication_provider(
                mode, add_urls.split(','), remove_urls.split(','),
                None, managerdn, passwd_user,
                searchbase, searchfilter, None,
                groupattr, name, add_domains.split(','),
                remove_domains.split(','), add_whitelist.split(','),
                remove_whitelist.split(','), searchscope, description,
                disable, None, maxpagesize)

    except IOError as e:
        common.format_err_msg_and_raise("update", "authentication provider",
                                        e[1], e.errno)

    except SOSError as e:
        common.format_err_msg_and_raise("update", "authentication provider",
                                        e.err_text, e.err_code)

    except ConfigParser.NoOptionError as e:
        common.format_err_msg_and_raise("update", "authentication provider",
                                        str(e), SOSError.NOT_FOUND_ERR)

    except (ConfigParser.ParsingError, ConfigParser.Error) as e:
        common.format_err_msg_and_raise("update", "authentication provider",
                                        str(e), SOSError.VALUE_ERR)


def defined_and_valid_value(fieldname, value, valid_list):
    if((value) and (value not in valid_list)):
                raise SOSError(
                    SOSError.VALUE_ERR,
                    fieldname + "can take values from among" + str(valid_list))


def list_authentication_provider(args):
    obj = Authentication(args.ip, args.port)
    try:
        uris = obj.list_authentication_provider()

        output = []

        for uri in uris:
            if(obj.show_authentication_provider_by_uri(uri['id'])):
                output.append(
                    obj.show_authentication_provider_by_uri(uri['id']))
        if(len(output) > 0):
            if(args.verbose):
                return common.format_json_object(output)
            elif(args.long):
                from common import TableGenerator
                TableGenerator(output, ['module/name', 'server_urls', 'mode',
                               'domains', 'group_attribute']).printTable()
            else:
                from common import TableGenerator
                TableGenerator(output, ['module/name', 'server_urls',
                               'mode']).printTable()
    except SOSError as e:
            if(e.err_code == SOSError.NOT_FOUND_ERR):
                raise SOSError(SOSError.NOT_FOUND_ERR,
                               "Tenant list failed: " + e.err_text)
            else:
                raise e


def authenticate_user(args):
    obj = Authentication(args.ip, args.port)
    try:
        if (args.username):
            if sys.stdin.isatty():
                passwd_user = getpass.getpass(prompt="Password : ")
            else:
                passwd_user = sys.stdin.readline().rstrip()
        else:
            raise SOSError(SOSError.CMD_LINE_ERR,
                           args.username + " : invalid username")
        res = obj.authenticate_user(args.username, passwd_user, args.cookiedir,
                                    args.cookiefile)


        print "authentication result: " + res                            
    except SOSError as e:
        raise e


def authenticate_parser(parent_subparser, sos_user, sos_cf, sos_cd, sos_ip, sos_port):
    # main authentication parser
    authenticate_parser = parent_subparser.add_parser(
        'authenticate',
        description='ECS authenticate CLI usage',
        conflict_handler='resolve',
        help='Authenticate ECS user')
    authenticate_parser.add_argument(
        '-cf', '-cookiefile',
        metavar='<cookiefile>',
        default=sos_cf,
        help='filename for storing cookie information',
        dest='cookiefile')
    authenticate_parser.add_argument(
        '-hostname', '-hn',
        metavar='<hostname>',
        default=sos_ip,
        dest='ip',
        help='Hostname (fully qualifiled domain name) of ECS')
    authenticate_parser.add_argument(
        '-port', '-po',
        type=int,
        metavar='<port_number>',
        default=sos_port,
        dest='port',
        help='port number of ECS')

    mandatory_args = authenticate_parser.add_argument_group(
        'mandatory arguments')

    mandatory_args.add_argument(
        '-u', '-username',
        metavar='<username>',
        help='username for login',
        default=sos_user,
        dest='username')

    mandatory_args.add_argument(
        '-d', '-cookiedir',
        metavar='<cookiedir>',
        help='cookie directory to store cookie files, if none is given then ECS_CLI_INSTALL_DIR must be set in ecscli.profile and will be used',
        default=sos_cd,
        dest='cookiedir')
    authenticate_parser.set_defaults(func=authenticate_user)


def add_auth_provider_parser(subcommand_parsers, common_parser):
    # add command parser
    add_auth_provider_parser = subcommand_parsers.add_parser(
        'add-provider',
        description='ECS Authentication Provider Add CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Add a Authentication Provider')

    mandatory_args = add_auth_provider_parser.add_argument_group(
        'mandatory arguments')

    mandatory_args.add_argument(
        '-configfile',
        metavar='<configfile>',
        help='config file for authentication provider',
        dest='configfile',
        required=True)

    add_auth_provider_parser.set_defaults(func=add_authentication_provider)


def show_auth_provider_parser(subcommand_parsers, common_parser):
    # show command parser
    show_auth_provider_parser = subcommand_parsers.add_parser(
        'show-provider',
        description='ECS Authentication Provider Show CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Show an Authentication Provider')

    mandatory_args = show_auth_provider_parser.add_argument_group(
        'mandatory arguments')

    mandatory_args.add_argument('-name',
                                metavar='<name>',
                                help='name of the authentication provider',
                                dest='name',
                                required=True)

    show_auth_provider_parser.add_argument('-xml',
                                           dest='xml',
                                           action='store_true',
                                           help='XML response')

    show_auth_provider_parser.set_defaults(func=show_authentication_provider)


def update_auth_provider_parser(subcommand_parsers, common_parser):
    # update command parser
    update_auth_provider_parser = subcommand_parsers.add_parser(
        'update',
        description='ECS Authentication Provider Update CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Update a Authentication Provider')

    mandatory_args = update_auth_provider_parser.add_argument_group(
        'mandatory arguments')

    mandatory_args.add_argument('-configfile',
                                metavar='<configfile>',
                                help='config file for authentication provider',
                                dest='configfile',
                                required=True)

    update_auth_provider_parser.set_defaults(
        func=update_authentication_provider)


def delete_auth_provider_parser(subcommand_parsers, common_parser):
    # delete command parser
    delete_auth_provider_parser = subcommand_parsers.add_parser(
        'delete-provider',
        description='ECS Authentication Provider delete CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Delete an Authentication Provider')

    mandatory_args = delete_auth_provider_parser.add_argument_group(
        'mandatory arguments')

    mandatory_args.add_argument('-name',
                                metavar='<name>',
                                help='name of the authentication provider',
                                dest='name',
                                required=True)

    delete_auth_provider_parser.set_defaults(
        func=delete_authentication_provider)


def list_auth_provider_parser(subcommand_parsers, common_parser):
    # update command parser
    list_auth_provider_parser = subcommand_parsers.add_parser(
        'list-providers',
        description='ECS Authentication Provider List CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='List Authentication Providers')

    list_auth_provider_parser.add_argument(
        '-verbose', '-v',
        action='store_true',
        help='List Authentication providers with details',
        dest='verbose')

    list_auth_provider_parser.add_argument(
        '-long', '-l',
        action='store_true',
        help='List Authentication providers with more details',
        dest='long')

    list_auth_provider_parser.set_defaults(func=list_authentication_provider)


def authentication_parser(parent_subparser, common_parser):
    # main authentication parser
    parser = parent_subparser.add_parser(
        'authentication',
        description='ECS Authentication Providers CLI usage',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Operations on Authentication')

    subcommand_parsers = parser.add_subparsers(help='Use One Of Commands')

    # authentication provider parser
    add_auth_provider_parser(subcommand_parsers, common_parser)

    show_auth_provider_parser(subcommand_parsers, common_parser)

    update_auth_provider_parser(subcommand_parsers, common_parser)

    delete_auth_provider_parser(subcommand_parsers, common_parser)

    list_auth_provider_parser(subcommand_parsers, common_parser)
