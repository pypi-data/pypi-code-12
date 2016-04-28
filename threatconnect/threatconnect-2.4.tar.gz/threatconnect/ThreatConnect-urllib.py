""" standard """
import base64
from datetime import datetime
import hashlib
import hmac
import json
import logging
import os
import re
import socket
import sys
import time
import urllib
import urllib2
import urlparse

""" third-party """
from requests import (exceptions, packages, Request, Session)
# disable ssl warning message
packages.urllib3.disable_warnings()

#
# memory testing
#
import psutil

""" custom """
from threatconnect.ErrorCodes import ErrorCodes

# tc config modules
from threatconnect.Config.FilterOperator import FilterSetOperator
from threatconnect.Config.ResourceType import ResourceType

from threatconnect.DnsResolutionObject import parse_dns_resolution
from threatconnect.IndicatorObject import parse_indicator
from threatconnect.GroupObject import parse_group
from threatconnect.OwnerObject import parse_owner
from threatconnect.VictimObject import parse_victim
from threatconnect.Resources.BatchJobs import BatchJobs, parse_batch_job

from threatconnect.ReportEntry import ReportEntry
from threatconnect.Report import Report
from threatconnect.Resources.Adversaries import Adversaries
from threatconnect.Resources.Bulk import Bulk
from threatconnect.Resources.BulkIndicators import BulkIndicators
from threatconnect.Resources.Documents import Documents
from threatconnect.Resources.Emails import Emails
from threatconnect.Resources.Groups import Groups
from threatconnect.Resources.Incidents import Incidents
from threatconnect.Resources.Indicators import Indicators
from threatconnect.Resources.Owners import Owners
from threatconnect.Resources.Threats import Threats
from threatconnect.Resources.Signatures import Signatures
from threatconnect.Resources.Victims import Victims


def tc_logger():
    """create temp logger"""
    tcl = logging.getLogger('threatconnect')
    tcl.setLevel(logging.CRITICAL)
    return tcl


class ThreatConnect:
    """ """

    def __init__(self, api_aid, api_sec, api_org, api_url):
        """ """
        # logger
        self.log_level = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL}
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(funcName)s:%(lineno)d)')
        self.tcl = tc_logger()

        # debugging
        self._memory_monitor = True

        # credentials
        self._api_aid = api_aid
        self._api_sec = api_sec

        # user defined values
        self._api_org = api_org
        self._api_url = api_url
        self._api_result_limit = 200

        # default values
        self._activity_log = 'false'
        self._api_request_timeout = 30
        self._api_retries = 5  # maximum of 5 minute window
        self._api_sleep = 59  # seconds
        self._proxies = {'https': None}
        self._enable_report = False

        # config items
        self._report = []
        self._verify_ssl = False

        # initialize request session handle
        self._session = Session()

        # instantiate report object
        self.report = Report()

        #
        # Memory Testing
        #
        self._p = psutil.Process(os.getpid())
        self._memory = self._p.memory_info().rss

    def _api_request_headers(self, ro):
        """ """
        timestamp = int(time.time())
        signature = "{0}:{1}:{2}".format(ro.path_url, ro.http_method, timestamp)
        # python 2.7, does not work on 3.x and not tested on 2.6
        # hmac_signature = hmac.new(self._api_sec, signature, digestmod=hashlib.sha256).digest()
        # authorization = 'TC {0}:{1}'.format(self._api_aid, base64.b64encode(hmac_signature))
        # python 3.x
        hmac_signature = hmac.new(self._api_sec.encode(), signature.encode(), digestmod=hashlib.sha256).digest()
        authorization = 'TC {0}:{1}'.format(self._api_aid, base64.b64encode(hmac_signature).decode())

        ro.add_header('Timestamp', timestamp)
        ro.add_header('Authorization', authorization)

    def api_filter_handler(self, resource_obj, filter_objs):
        """ """
        data_set = None

        if not filter_objs:
            # build api call (no filters)
            default_request_object = resource_obj.default_request_object
            data_set = self.api_response_handler(resource_obj, default_request_object)
        else:
            #
            # process each filter added to the resource object for retrieve
            #
            first_run = True

            #
            # each resource object can have x filter objects with an operator to join or intersect results
            #
            for filter_obj in filter_objs:

                obj_list = []  # temp storage for results on individual filter objects
                owners = filter_obj.owners
                if len(owners) == 0:  # handle filters with no owners
                    owners = [self._api_org]  # use default org

                # iterate through all owners
                for o in owners:
                    self.tcl.debug('owner: {0!s}'.format(o))
                    if len(filter_obj) > 0:
                        # request object are for api filters
                        for ro in filter_obj:
                            if ro.owner_allowed:
                                ro.set_owner(o)
                            results = self.api_response_handler(resource_obj, ro)

                            if ro.resource_type not in [ResourceType.OWNERS,
                                                        ResourceType.VICTIMS,
                                                        ResourceType.BATCH_JOBS]:
                                # TODO: should this be done?
                                # post filter owners
                                for obj in results:
                                    if obj.owner_name.upper() != o.upper():
                                        results.remove(obj)

                            obj_list.extend(results)
                    else:
                        ro = filter_obj.default_request_object
                        if ro.owner_allowed:
                            ro.set_owner(o)
                        results = self.api_response_handler(resource_obj, ro)

                        if ro.resource_type not in [ResourceType.OWNERS, ResourceType.VICTIMS]:
                            # TODO: should this be done?
                            # post filter owners
                            for obj in results:
                                if obj.owner_name != o:
                                    results.remove(obj)

                        obj_list.extend(results)

                    #
                    # post filters
                    #
                    pf_obj_set = set(obj_list)
                    self.tcl.debug('count before post filter: {0:d}'.format(len(obj_list)))
                    for pfo in filter_obj.post_filters:
                        self.tcl.debug('pfo: {0!s}'.format(pfo))

                        #
                        # Report Entry
                        #
                        report_entry = ReportEntry()
                        report_entry.add_post_filter_object(pfo)

                        # current post filter method
                        filter_method = getattr(resource_obj, pfo.method)

                        # current post filter results
                        post_filter_results = set(filter_method(pfo.filter, pfo.operator, pfo.description))

                        pf_obj_set = pf_obj_set.intersection(post_filter_results)

                        self.report.add(report_entry)

                    # set obj_list to post_filter results
                    if filter_obj.post_filters_len > 0:
                        obj_list = list(pf_obj_set)

                    self.tcl.debug('count after post filter: {0:d}'.format(len(obj_list)))

                    # no need to join or intersect on first run
                    if first_run:
                        data_set = set(obj_list)
                        first_run = False
                        continue

                #
                # depending on the filter type the result will be intersected or joined
                #
                if filter_obj.operator is FilterSetOperator.AND:
                    data_set = data_set.intersection(obj_list)
                elif filter_obj.operator is FilterSetOperator.OR:
                    data_set.update(set(obj_list))

        #
        # only add to report if these results should be tracked (exclude attribute, tags, etc)
        #
        self.report.add_filtered_results(len(data_set))

        #
        # after intersection or join add the objects to the resource object
        #
        for obj in data_set:
            resource_obj.add_obj(obj)

    def api_request2(self, ro):
        """ """
        self.print_mem('start of api_request2')
        api_response = None
        fail_msg = None
        h_content_length = None
        h_content_type = None
        start = datetime.now()

        #
        # enable activity log
        #
        # request_object.enable_activity_mode()

        #
        # prepare request
        #
        url = '{0!s}{1!s}'.format(self._api_url, ro.request_uri)
        payload = urllib.urlencode(ro.payload)
        full_url = '{0!s}?{1!s}'.format(url, payload)
        parsed_url = urlparse.urlparse(full_url)
        path_url = '{0!s}?{1!s}'.format(parsed_url.path, parsed_url.query)

        #
        # generate headers
        #
        ro.set_path_url(path_url)
        self._api_request_headers(ro)

# bcs
        #
        # proxy handler
        #
        if self._proxies['https'] is not None:
            proxy_handler = urllib2.ProxyHandler(self._proxies)
            # proxy_auth_handler = urllib2.ProxyBasicAuthHandler()
            # proxy_auth_handler.add_password('realm', 'host', 'username', 'password')
            # opener = urllib2.build_opener(proxy_handler, proxy_auth_handler)
            opener = urllib2.build_opener(proxy_handler)
            urllib2.install_opener(opener)

        #
        # request
        #
        req = urllib2.Request(full_url, headers=ro.headers)

        # print('url {0}'.format(url))
        # print('payload {0}'.format(payload))
        # print('headers {0}'.format(ro.headers))

        response = urllib2.urlopen(req)
        data = response.read()
        # print('response: {0}'.format(json.dumps(data)))
        print('Request Time: {0!s}'.format(datetime.now() - start))
        self.print_mem('end of api_request2')
        return data

        #
        # Debug
        #
        self.tcl.debug('request_object: {0!s}'.format(ro))
        self.tcl.debug('url: {0!s}'.format(url))
        self.tcl.debug('path url: {0!s}'.format(request_prepped.path_url))

        #
        # api request (gracefully handle temporary communications issues with the API)
        #
        for i in range(1, self._api_retries + 1, 1):
            try:
                api_response = self._session.send(
                    request_prepped, verify=self._verify_ssl, timeout=self._api_request_timeout,
                    proxies=self._proxies, stream=False)
                break
            except exceptions.ReadTimeout as e:
                self.tcl.error('Error: {0!s}'.format(e))
                self.tcl.error('The server may be experiencing delays at the moment.')
                self.tcl.info('Pausing for {0!s} seconds to give server time to catch up.'.format(self._api_sleep))
                time.sleep(self._api_sleep)
                self.tcl.info('Retry {0!s} ....'.format(i))

                if i == self._api_retries:
                    self.tcl.critical('Exiting: {0!s}'.format(e))
                    raise RuntimeError(e)
            except exceptions.ConnectionError as e:
                self.tcl.error('Error: {0!s}'.format(e))
                self.tcl.error('Connection Error. The server may be down.')
                self.tcl.info('Pausing for {0!s} seconds to give server time to catch up.'.format(self._api_sleep))
                time.sleep(self._api_sleep)
                self.tcl.info('Retry {0!s} ....'.format(i))
                if i == self._api_retries:
                    self.tcl.critical('Exiting: {0!s}'.format(e))
                    raise RuntimeError(e)
            except socket.error as e:
                self.tcl.critical('Exiting: {0!s}'.format(e))
                raise RuntimeError(e)

        #
        # header values
        #
        if 'content-length' in api_response.headers:
            h_content_length = api_response.headers['content-length']
        if 'content-type' in api_response.headers:
            h_content_type = api_response.headers['content-type']

        #
        # raise exception on *critical* errors
        #
        non_critical_errors = [
            b'The MD5 for this File is invalid, a File with this MD5 already exists',  # 400 (application/json)
            b'The SHA-1 for this File is invalid, a File with this SHA-1 already exists',  # 400 (application/json)
            b'The SHA-256 for this File is invalid, a File with this SHA-256 already exists',  # 400 (application/json)
            b'The requested resource was not found',  # 404 (application/json)
            b'Could not find resource for relative',  # 500 (text/plain)
            b'The requested Security Label was not removed - access was denied',  # 401 (application/json)
        ]

        #
        # TODO: work out some logic to improve the API error handling, possible area where API could improve
        #

        # valid status codes 200, 201, 202
        # if api_response.status_code in [400, 401, 403, 500, 503]:
        if api_response.status_code not in [200, 201, 202]:
            # check for non critical errors that have bad status codes
            nce_found = False
            fail_msg = api_response.content
            for nce in non_critical_errors:
                # api_response_dict['message'] not in non_critical_errors:
                if re.findall(nce, api_response.content):
                    nce_found = True
                    break

            if ro.failure_callback is not None:
                ro.failure_callback(api_response.status_code)

            # raise error on bad status codes that are not defined as nce
            if not nce_found:
                self.tcl.critical('Status Code: {0:d}'.format(api_response.status_code))
                self.tcl.critical('Failed API Response: {0!s}'.format(api_response.content))
                if ro.failure_callback is not None:
                    ro.failure_callback(api_response.status_code)
                raise RuntimeError(api_response.content)

        #
        # set response encoding (best guess)
        #
        if api_response.encoding is None:
            api_response.encoding = api_response.apparent_encoding

        #
        # Debug
        #
        self.tcl.debug('url: %s', api_response.url)
        self.tcl.debug('status_code: %s', api_response.status_code)
        self.tcl.debug('content-length: %s', h_content_length)
        self.tcl.debug('content-type: %s', h_content_type)

        #
        # Report
        #
        self.report.add_api_call()  # count api calls
        self.report.add_request_time(datetime.now() - start)
        self.tcl.debug('Request Time: {0!s}'.format(datetime.now() - start))

        if self._enable_report:
            report_entry = ReportEntry()
            report_entry.add_request_object(ro)
            report_entry.set_request_url(api_response.url)
            report_entry.set_status_code(api_response.status_code)
            report_entry.set_failure_msg(fail_msg)
            self.report.add(report_entry)

        #
        # return response
        #
        # self.print_mem('end _api_request')
        return api_response

    def api_request(self, ro):
        """ """
        self.print_mem('start of api_request2')
        api_response = None
        fail_msg = None
        h_content_length = None
        h_content_type = None
        start = datetime.now()

        #
        # enable activity log
        #
        # request_object.enable_activity_mode()

        #
        # prepare request
        #
        url = '{0!s}{1!s}'.format(self._api_url, ro.request_uri)
        api_request = Request(ro.http_method, url, data=ro.body, params=ro.payload)
        request_prepped = api_request.prepare()

        #
        # generate headers
        #
        ro.set_path_url(request_prepped.path_url)
        self._api_request_headers(ro)
        request_prepped.prepare_headers(ro.headers)

        #
        # Debug
        #
        self.tcl.debug('request_object: {0!s}'.format(ro))
        self.tcl.debug('url: {0!s}'.format(url))
        self.tcl.debug('path url: {0!s}'.format(request_prepped.path_url))

        #
        # api request (gracefully handle temporary communications issues with the API)
        #
        for i in range(1, self._api_retries + 1, 1):
            try:
                api_response = self._session.send(
                    request_prepped, verify=self._verify_ssl, timeout=self._api_request_timeout,
                    proxies=self._proxies, stream=False)
                break
            except exceptions.ReadTimeout as e:
                self.tcl.error('Error: {0!s}'.format(e))
                self.tcl.error('The server may be experiencing delays at the moment.')
                self.tcl.info('Pausing for {0!s} seconds to give server time to catch up.'.format(self._api_sleep))
                time.sleep(self._api_sleep)
                self.tcl.info('Retry {0!s} ....'.format(i))

                if i == self._api_retries:
                    self.tcl.critical('Exiting: {0!s}'.format(e))
                    raise RuntimeError(e)
            except exceptions.ConnectionError as e:
                self.tcl.error('Error: {0!s}'.format(e))
                self.tcl.error('Connection Error. The server may be down.')
                self.tcl.info('Pausing for {0!s} seconds to give server time to catch up.'.format(self._api_sleep))
                time.sleep(self._api_sleep)
                self.tcl.info('Retry {0!s} ....'.format(i))
                if i == self._api_retries:
                    self.tcl.critical('Exiting: {0!s}'.format(e))
                    raise RuntimeError(e)
            except socket.error as e:
                self.tcl.critical('Exiting: {0!s}'.format(e))
                raise RuntimeError(e)

        #
        # header values
        #
        if 'content-length' in api_response.headers:
            h_content_length = api_response.headers['content-length']
        if 'content-type' in api_response.headers:
            h_content_type = api_response.headers['content-type']

        #
        # raise exception on *critical* errors
        #
        non_critical_errors = [
            b'The MD5 for this File is invalid, a File with this MD5 already exists',  # 400 (application/json)
            b'The SHA-1 for this File is invalid, a File with this SHA-1 already exists',  # 400 (application/json)
            b'The SHA-256 for this File is invalid, a File with this SHA-256 already exists',  # 400 (application/json)
            b'The requested resource was not found',  # 404 (application/json)
            b'Could not find resource for relative',  # 500 (text/plain)
            b'The requested Security Label was not removed - access was denied',  # 401 (application/json)
        ]

        #
        # TODO: work out some logic to improve the API error handling, possible area where API could improve
        #

        # valid status codes 200, 201, 202
        # if api_response.status_code in [400, 401, 403, 500, 503]:
        if api_response.status_code not in [200, 201, 202]:
            # check for non critical errors that have bad status codes
            nce_found = False
            fail_msg = api_response.content
            for nce in non_critical_errors:
                # api_response_dict['message'] not in non_critical_errors:
                if re.findall(nce, api_response.content):
                    nce_found = True
                    break

            if ro.failure_callback is not None:
                ro.failure_callback(api_response.status_code)

            # raise error on bad status codes that are not defined as nce
            if not nce_found:
                self.tcl.critical('Status Code: {0:d}'.format(api_response.status_code))
                self.tcl.critical('Failed API Response: {0!s}'.format(api_response.content))
                if ro.failure_callback is not None:
                    ro.failure_callback(api_response.status_code)
                raise RuntimeError(api_response.content)

        #
        # set response encoding (best guess)
        #
        if api_response.encoding is None:
            api_response.encoding = api_response.apparent_encoding

        #
        # Debug
        #
        self.tcl.debug('url: %s', api_response.url)
        self.tcl.debug('status_code: %s', api_response.status_code)
        self.tcl.debug('content-length: %s', h_content_length)
        self.tcl.debug('content-type: %s', h_content_type)

        #
        # Report
        #
        self.report.add_api_call()  # count api calls
        self.report.add_request_time(datetime.now() - start)
        self.tcl.debug('Request Time: {0!s}'.format(datetime.now() - start))

        if self._enable_report:
            report_entry = ReportEntry()
            report_entry.add_request_object(ro)
            report_entry.set_request_url(api_response.url)
            report_entry.set_status_code(api_response.status_code)
            report_entry.set_failure_msg(fail_msg)
            self.report.add(report_entry)

        #
        # return response
        #
        # self.print_mem('end _api_request')
        print('Request Time: {0!s}'.format(datetime.now() - start))
        self.print_mem('end of api_request2')
        return api_response

    def api_response_handler(self, resource_obj, ro):
        """ """
        #
        # initialize vars
        #
        api_response_dict = {}
        obj_list = []
        # only track filter counts on request from this method
        ro.enable_track()

        #
        # debug
        #
        self.tcl.debug('Results Limit: {0!s}'.format(self._api_result_limit))

        # only resource supports pagination
        if ro.resource_pagination:
            ro.set_result_limit(self._api_result_limit)
            ro.set_result_start(0)

        while ro.remaining_results > 0:
            #
            # api request
            #
            api_response = self.api_request(ro)
            # self.tcl.debug('Results Content: {0!s}'.format(api_response.content))
            self.tcl.debug('Status Code: {0!s}'.format(api_response.status_code))
            self.tcl.debug('Content Type: {0!s}'.format(api_response.headers['content-type']))

            #
            # Process API response
            #
            if api_response.headers['content-type'] == 'application/json':
                api_response_dict = api_response.json()
                # self.print_mem('after building dict')

                # try and free memory for next api request
                api_response.close()
                del api_response  # doesn't appear to clear memory

                #
                # BULK INDICATOR (does not have status)
                #
                if 'indicator' in api_response_dict:
                    if ro.resource_type == ResourceType.INDICATORS:
                        data = api_response_dict['indicator']
                        for item in data:
                            obj_list.append(parse_indicator(item, resource_obj, ro.description, ro.request_uri))

                            if len(obj_list) % 500 == 0:
                                self.tcl.debug('obj_list len: {0!s}'.format(len(obj_list)))
                                self.print_mem('bulk process - {0:d} objects'.format(len(obj_list)))

                elif api_response_dict['status'] == 'Failure':
                    # handle failed request (404 Resource not Found)
                    if 'message' in api_response_dict:
                        self.tcl.error('{0!s} "{1!s}"'.format(api_response_dict['message'], ro.description))
                    ro.set_remaining_results(0)
                    continue

                #
                # ADVERSARIES
                #
                elif ro.resource_type == ResourceType.ADVERSARIES:
                    data = api_response_dict['data']['adversary']
                    if not isinstance(data, list):
                        data = [data]  # for single results to be a list
                    for item in data:
                        obj_list.append(
                            parse_group(item, ResourceType.ADVERSARIES, resource_obj, ro.description, ro.request_uri))

                #
                # INDICATORS
                #
                elif ro.resource_type == ResourceType.INDICATORS:
                    data = api_response_dict['data']['indicator']
                    if not isinstance(data, list):
                        data = [data]  # for single results to be a list
                    for item in data:
                        obj_list.append(parse_indicator(item, resource_obj, ro.description, ro.request_uri))

                #
                # ADDRESSES
                #
                elif ro.resource_type == ResourceType.ADDRESSES:
                    data = api_response_dict['data']['address']
                    if not isinstance(data, list):
                        data = [data]  # for single results to be a list
                    for item in data:
                        obj_list.append(parse_indicator(item, resource_obj, ro.description, ro.request_uri))

                #
                # DOCUMENTS
                #
                elif ro.resource_type == ResourceType.DOCUMENTS:
                    data = api_response_dict['data']['document']
                    if not isinstance(data, list):
                        data = [data]  # for single results to be a list
                    for item in data:
                        obj_list.append(
                            parse_group(item, ResourceType.DOCUMENTS, resource_obj, ro.description, ro.request_uri))

                #
                # EMAILS
                #
                elif ro.resource_type == ResourceType.EMAILS:
                    data = api_response_dict['data']['email']
                    if not isinstance(data, list):
                        data = [data]  # for single results to be a list
                    for item in data:
                        obj_list.append(
                            parse_group(item, ResourceType.EMAILS, resource_obj, ro.description, ro.request_uri))

                #
                # EMAIL ADDRESSES
                #
                elif ro.resource_type == ResourceType.EMAIL_ADDRESSES:
                    data = api_response_dict['data']['emailAddress']
                    if not isinstance(data, list):
                        data = [data]  # for single results to be a list
                    for item in data:
                        obj_list.append(parse_indicator(item, resource_obj, ro.description, ro.request_uri))

                #
                # GROUPS
                #
                elif ro.resource_type == ResourceType.GROUPS:
                    data = api_response_dict['data']['group']
                    if not isinstance(data, list):
                        data = [data]  # for single results to be a list
                    for item in data:
                        obj_list.append(
                            parse_group(item, ResourceType.GROUPS, resource_obj, ro.description, ro.request_uri))

                #
                # FILES
                #
                elif ro.resource_type == ResourceType.FILES:
                    data = api_response_dict['data']['file']
                    if not isinstance(data, list):
                        data = [data]  # for single results to be a list
                    for item in data:
                        obj_list.append(parse_indicator(item, resource_obj, ro.description, ro.request_uri))

                #
                # HOSTS
                #
                elif ro.resource_type == ResourceType.HOSTS:
                    data = api_response_dict['data']['host']
                    if not isinstance(data, list):
                        data = [data]  # for single results to be a list
                    for item in data:
                        obj_list.append(parse_indicator(item, resource_obj, ro.description, ro.request_uri))

                #
                # DNSResolutions
                #
                elif ro.resource_type == ResourceType.DNS_RESOLUTIONS:
                    data = api_response_dict['data']['dnsResolution']
                    if not isinstance(data, list):
                        data = [data]  # for single results to be a list
                    for item in data:
                        if 'addresses' in item:  # don't process dns resolutions that have no addresses
                            obj_list.append(parse_dns_resolution(item))
                #
                # INCIDENTS
                #
                elif ro.resource_type == ResourceType.INCIDENTS:
                    data = api_response_dict['data']['incident']
                    if not isinstance(data, list):
                        data = [data]  # for single results to be a list
                    for item in data:
                        obj_list.append(
                            parse_group(item, ResourceType.INCIDENTS, resource_obj, ro.description, ro.request_uri))

                #
                # OWNERS
                #
                elif ro.resource_type == ResourceType.OWNERS:
                    data = api_response_dict['data']['owner']
                    if not isinstance(data, list):
                        data = [data]  # for single results to be a list
                    for item in data:
                        obj_list.append(
                            parse_owner(item, resource_obj, ro.description, ro.request_uri))

                #
                # SIGNATURES
                #
                elif ro.resource_type == ResourceType.SIGNATURES:
                    data = api_response_dict['data']['signature']
                    if not isinstance(data, list):
                        data = [data]  # for single results to be a list
                    for item in data:
                        obj_list.append(
                            parse_group(item, ResourceType.SIGNATURES, resource_obj, ro.description, ro.request_uri))

                #
                # THREATS
                #
                elif ro.resource_type == ResourceType.THREATS:
                    data = api_response_dict['data']['threat']
                    if not isinstance(data, list):
                        data = [data]  # for single results to be a list
                    for item in data:
                        obj_list.append(
                            parse_group(item, ResourceType.THREATS, resource_obj, ro.description, ro.request_uri))

                #
                # URLS
                #
                elif ro.resource_type == ResourceType.URLS:
                    data = api_response_dict['data']['url']
                    if not isinstance(data, list):
                        data = [data]  # for single results to be a list
                    for item in data:
                        obj_list.append(parse_indicator(item, resource_obj, ro.description, ro.request_uri))

                #
                # VICTIMS
                #
                elif ro.resource_type == ResourceType.VICTIMS:
                    data = api_response_dict['data']['victim']
                    if not isinstance(data, list):
                        data = [data]  # for single results to be a list
                    for item in data:
                        # victims data comes back with no owner, manually add owner here
                        item['owner'] = ro.owner
                        obj_list.append(parse_victim(item, resource_obj, ro.description, ro.request_uri))

                #
                # BatchJobs
                #
                elif ro.resource_type == ResourceType.BATCH_JOBS:
                    data = api_response_dict['data']['batchStatus']
                    if not isinstance(data, list):
                        data = [data]  # for single results to be a list
                    for item in data:
                        # victims data comes back with no owner, manually add owner here
                        item['owner'] = ro.owner
                        obj_list.append(parse_batch_job(item, resource_obj, ro.description, ro.request_uri))

                #
                # memory testing
                #
                self.print_mem('pagination - {0:d} objects'.format(len(obj_list)))

            elif api_response.headers['content-type'] == 'text/plain':
                self.tcl.error('{0!s} "{1!s}"'.format(api_response.content, ro.description))
                ro.set_remaining_results(0)
                continue

            # add_obj resource_pagination if required
            if ro.resource_pagination:
                # get the number of results returned by the api
                if ro.result_start == 0:
                    ro.set_remaining_results(api_response_dict['data']['resultCount'] - ro.result_limit)
                else:
                    ro.set_remaining_results(ro.remaining_results - ro.result_limit)

                # increment the start position
                ro.set_result_start(ro.result_start + ro.result_limit)
            else:
                ro.set_remaining_results(0)

        self.tcl.debug('Result Count: {0!s}'.format(len(obj_list)))
        self.report.add_unfiltered_results(len(obj_list))
        return obj_list

    #
    # api / sdk settings
    #

    def result_pagination(self, ro, identifier):
        data = []

        ro.set_result_limit(self._api_result_limit)
        ro.set_result_start(0)

        while ro.remaining_results > 0:
            api_response = self.api_request(ro)

            if api_response.headers['content-type'] == 'application/json':
                api_response_dict = api_response.json()
                if api_response_dict['status'] == 'Success':
                    data.extend(api_response_dict['data'][identifier])

            # get the number of results returned by the api
            if ro.result_start == 0:
                ro.set_remaining_results(api_response_dict['data']['resultCount'] - ro.result_limit)
            else:
                ro.set_remaining_results(ro.remaining_results - ro.result_limit)

            # increment the start position
            ro.set_result_start(ro.result_start + ro.result_limit)

        return data

    def print_mem(self, msg):
        if self._memory_monitor:
            current_mem = self._p.memory_info().rss
            # self.tcl.info('Memory ({0!s}) - Delta {1:d} Bytes'.format(msg, current_mem - self._memory))
            # self.tcl.info('Memory ({0!s}) - RSS {1:d} Bytes'.format(msg, current_mem))
            print('Memory ({0!s}) - Delta {1:d} Bytes'.format(msg, current_mem - self._memory))
            print('Memory ({0!s}) - RSS {1:d} Bytes'.format(msg, current_mem))
            self._memory = current_mem

    def report_enable(self):
        """ """
        self._enable_report = True

    def report_disable(self):
        """ """
        self._enable_report = False

    def set_activity_log(self, data_bool):
        """ enable or disable api activity log """
        if isinstance(data_bool, bool):
            data_bool = str(data_bool).lower()

        if data_bool in ['true', 'false']:
            self._activity_log = data_bool

    def set_api_request_timeout(self, data_int):
        """ set timeout value for the requests module """
        if isinstance(data_int, int):
            self._api_request_timeout = data_int
        else:
            raise AttributeError(ErrorCodes.e0110.value.format(data_int))

    def set_api_retries(self, data):
        """ set the number of api retries before exception is raised """
        if isinstance(data, int):
            self._api_retries = data
        else:
            raise AttributeError(ErrorCodes.e0120.value.format(data))

    def set_api_sleep(self, data):
        """ set the amount of time between retries """
        if isinstance(data, int):
            self._api_sleep = data
        else:
            raise AttributeError(ErrorCodes.e0130.value.format(data))

    def set_api_result_limit(self, data_int):
        """ set the number of result to return per api request (500 max) """
        if isinstance(data_int, int):
            self._api_result_limit = data_int
        else:
            raise AttributeError(ErrorCodes.e0140.value.format(data_int))

    def set_proxies(self, proxy_address, proxy_port, proxy_user=None, proxy_pass=None):
        """ define proxy server to use with the requests module """
        # "http": "http://user:pass@10.10.1.10:3128/",

        # TODO: add validation
        if proxy_user is not None and proxy_pass is not None:
            self._proxies['https'] = '{0!s}:{1!s}@{2!s}:{3!s}'.format(proxy_user, proxy_pass, proxy_address, proxy_port)
        else:
            self._proxies['https'] = '{0!s}:{1!s}'.format(proxy_address, proxy_port)

    def set_tcl_file(self, fqpn, level='info'):
        """ set the log file destination and log level """
        file_path = os.path.dirname(fqpn)
        if os.access(file_path, os.W_OK):
            if self.tcl.level > self.log_level[level]:
                self.tcl.setLevel(self.log_level[level])
            fh = logging.FileHandler(fqpn)
            # fh.set_name('tc_log_file')  # not supported in python 2.6
            if level in self.log_level.keys():
                fh.setLevel(self.log_level[level])
            else:
                fh.setLevel(self.log_level['info'])
            fh.setFormatter(self.formatter)
            self.tcl.addHandler(fh)

    # def set_tcl_level(self, level):
    #     """ """
    #     if level in self.log_level.keys():
    #         if self.tcl.level > self.log_level[level]:
    #             self.tcl.setLevel(self.log_level[level])
    #         self.tcl.handlers[0].setLevel(self.log_level[level])

    def set_tcl_console_level(self, level):
        """ set the console log level """
        if level in self.log_level.keys():
            if self.tcl.level > self.log_level[level]:
                self.tcl.setLevel(self.log_level[level])
            ch = logging.StreamHandler()
            # ch.set_name('console')  # not supported in python 2.6
            ch.setLevel(self.log_level[level])
            ch.setFormatter(self.formatter)
            self.tcl.addHandler(ch)

    #
    # Resources
    #

    def adversaries(self):
        """ return an adversary container object """
        return Adversaries(self)

    def bulk(self):
        """ return a bulk container object """
        return Bulk(self)

    def bulk_indicators(self):
        """ return a bulk indicator container object """
        return BulkIndicators(self)

    def documents(self):
        """ return a document container object """
        return Documents(self)

    def emails(self):
        """ return an email container object """
        return Emails(self)

    def groups(self):
        """ return an group container object """
        return Groups(self)

    def incidents(self):
        """ return an incident container object """
        return Incidents(self)

    def indicators(self):
        """ return an indicator container object """
        return Indicators(self)

    def owners(self):
        """ return an owner container object """
        return Owners(self)

    def signatures(self):
        """ return a signature container object """
        return Signatures(self)

    def threats(self):
        """ return a threat container object """
        return Threats(self)

    def victims(self):
        """ return a victim container object """
        return Victims(self)

    def batch_jobs(self):
        return BatchJobs(self)
