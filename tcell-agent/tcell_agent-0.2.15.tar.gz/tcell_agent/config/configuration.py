# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals
from __future__ import print_function

import json
import os.path
import socket
import uuid
import os
import errno
import yaml
import logging
import logging.handlers
import traceback

DEFAULT_CONFIG_FILENAME = "tcell_agent.config"
DEFAULT_HOME = "tcell/"

def mkdir_p(path):
    """http://stackoverflow.com/a/600612/190597 (tzot)"""
    try:
        os.makedirs(path, exist_ok=True)  # Python>3.2
    except TypeError:
        try:
            os.makedirs(path)
        except OSError as exc: # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else: raise

class TcellAgentConfiguration(object):
    """docstring for ClassName"""
    def get_configuration_logger(self, log_filename):
        new_logger = logging.getLogger("tcell_agent_configuration")
        formatter = logging.Formatter('%(asctime)s - %(name)s -- [%(levelname)s]: %(message)s')

        fh = logging.handlers.RotatingFileHandler(
                  log_filename, maxBytes=10*1024*1024, backupCount=5)
        fh.setFormatter(formatter)

        new_logger.setLevel("INFO")
        new_logger.addHandler(fh)
        return new_logger

    def __init__(self, filename=DEFAULT_CONFIG_FILENAME):
        self.tcell_agent_home = './tcell_agent'
        self.tcell_agent_log_home = None
        self.tcell_agent_config = None

        self.allow_unencrypted_appsensor_payloads = \
            (os.environ.get('TCELL_AGENT_ALLOW_UNENCRYPTED_APPSENSOR_PAYLOADS') in [True, "true", "1"]) or \
            (os.environ.get('TCELL_AGENT_ALLOW_UNENCRYPTED_APPFIREWALL_PAYLOADS') in [True, "true", "1"])

        self.max_data_ex_db_records_per_request = 1000

        self.version = 0
        self.app_id = None
        self.api_key = None
        self.tcell_api_url = "https://api.tcell.io/api/v1"
        self.tcell_input_url = "https://input.tcell.io/api/v1"
        self.company = None
        self.uuid = str(uuid.uuid4())
        self.host_identifier = None
        self.preload_policy_filename = None
        self.fetch_policies_from_tcell = True
        self.instrument_for_events = True
        self.hmac_key = None
        self.logging_options = {}
        self.reverse_proxy = True
        self.reverse_proxy_ip_address_header = None

        try:
            self.demo_mode = bool(os.environ.get('TCELL_DEMOMODE', None))
        except:
            self.demo_mode = False

        try:
            self.event_batch_size_limit = int(os.environ.get('TCELL_EVENT_SIZE_BATCH_LIMIT', 100))
        except:
            self.event_batch_size_limit = 100
        self.event_time_limit_seconds = 15

        self.event_queue_intake_size = 1000

        self.js_agent_api_base_url = None
        self.js_agent_url = "https://api.tcell.io/tcellagent.min.js"

        self.tcell_home = os.environ.get("TCELL_AGENT_HOME", DEFAULT_HOME)
        self.cache_folder = os.path.join(self.tcell_home, 'cache/')
        self.log_directory = os.environ.get("TCELL_AGENT_LOG_DIR", os.path.join(self.tcell_home, "logs/"))
        self.log_filename = os.path.join(self.log_directory, "tcell_agent.log")

        mkdir_p(self.tcell_home)
        mkdir_p(self.cache_folder)
        mkdir_p(self.log_directory)

        config_filename = os.path.abspath(os.environ.get("TCELL_AGENT_CONFIG",filename))
        backup_check_config_filename = os.path.abspath(os.path.join("tcell",filename))

        config_logger = self.get_configuration_logger(self.log_filename)

        config_logger.info("Checking for configuration file: '" + config_filename + "'")

        try:
            if os.path.isfile(config_filename) == False:
                config_logger.info("Checking for configuration file: '" + backup_check_config_filename + "'")
                if os.path.isfile(backup_check_config_filename) == True:
                    config_filename = backup_check_config_filename
                else:
                    config_filename = None

            if config_filename != None:
                if os.access(config_filename, os.R_OK) == False:
                    print("tCell.io Agent: [Error] Permission denied opening config file.")
                    config_logger.error("Permission denied for file '" + config_filename + "'")
                else:
                    with open(config_filename, "r") as data_file:
                        json_data = self.filter_commentlines(data_file.read())
                        try:
                            config_json = json.loads(json_data)
                            self.read_config(config_json)
                        except:
                            print("tCell.io Agent: [Error] Could not parse json in config file.")
                            traceback.print_exc()
                            config_logger.exception("Could not parse json in config file.")
            else:
                config_logger.info("Configuration file not found, using environmental variables.")
        except Exception as ex:
            print("Exception loading configuration file.")
            print(ex)
            config_logger.exception("Exception loading configuration file.")
            raise

        config_logger.info("Checking configuration environmental variables.")

        self.app_id = os.environ.get("TCELL_AGENT_APP_ID", self.app_id)
        self.api_key = os.environ.get("TCELL_AGENT_API_KEY", self.api_key)
        self.host_identifier = os.environ.get("TCELL_AGENT_HOST_IDENTIFIER", self.host_identifier)

        if self.app_id is None:
            config_logger.warn("tCell.io APP ID not set by file or environmental variable.")
        if self.api_key is None:
            config_logger.warn("tCell.io API Key not set by file or environmental variable.")

        self.load_app_sensor_restrictions()

    def filter_commentlines(self, json_data):
        """
        Removes full line comments from json to provide trivial support for commenting. Does not remove
        end of line comments.
        :param json_data: A json text string
        :return: json text without comments
        """
        return "\n".join(l for l in json_data.split("\n") if not l.strip().startswith("//"))

    def read_config(self, config_json):
        if "version" not in config_json:
            self.version = 0
            self.company = config_json.get("COMPANY")
            self.app_id = config_json.get("APP_NAME")
            self.api_key = config_json.get("API_KEY")
            self.tcell_input_url = config_json.get("TCELL_INPUT_URL","https://input.tcell.io:8008")
            self.host_identifier = socket.getfqdn()
        else:
            self.version = config_json["version"]
            if self.version == 1:
                applications = config_json["applications"]
                if applications and len(applications) > 0:
                    application_config_json = applications[0] # Get the first application for now
                    v0_app_id = application_config_json.get("name")
                    self.app_id = application_config_json.get("app_id", v0_app_id)
                    self.api_key = application_config_json.get("api_key")
                    self.enabled = application_config_json.get("enabled",True)
                    self.fetch_policies_from_tcell = application_config_json.get("fetch_policies_from_tcell", True)
                    self.preload_policy_filename = application_config_json.get("preload_policy_filename")
                    self.logging_options = application_config_json.get("logging_options", self.logging_options)
                    self.instrument_for_events = application_config_json.get("instrument_for_events",True)
                    new_api_url = application_config_json.get("tcell_api_url",  None)
                    if (new_api_url is not None and new_api_url != self.tcell_api_url):
                        # Change default jsagent
                        self.js_agent_api_base_url = new_api_url
                        self.tcell_api_url = new_api_url

                    self.tcell_input_url = application_config_json.get("tcell_input_url", self.tcell_input_url)
                    host_identifier = application_config_json.get("host_identifier")
                    if host_identifier is None:
                        host_identifier = socket.getfqdn()
                    self.host_identifier = host_identifier

                    self.hmac_key = application_config_json.get("hmac_key")

                    self.js_agent_api_base_url = application_config_json.get("js_agent_api_base_url",self.js_agent_api_base_url)
                    self.js_agent_url = application_config_json.get("js_agent_url",self.js_agent_url)

                    # hidden
                    try:
                        self.event_batch_size_limit = int(application_config_json.get('event_batch_size_limit', self.event_batch_size_limit))
                    except:
                        pass

                    self.allow_unencrypted_appsensor_payloads = application_config_json.get('allow_unencrypted_appsensor_payloads', self.allow_unencrypted_appsensor_payloads) 
                    self.allow_unencrypted_appsensor_payloads = application_config_json.get('allow_unencrypted_appfirewall_payloads', self.allow_unencrypted_appsensor_payloads) 

                    (os.environ.get('TCELL_AGENT_ALLOW_APPSENSOR_PAYLOADS', '0')=='1')

                    data_exposure = application_config_json.get('data_exposure', {})
                    self.max_data_ex_db_records_per_request = data_exposure.get('max_data_ex_db_records_per_request', self.max_data_ex_db_records_per_request)

                    self.reverse_proxy = application_config_json.get('reverse_proxy', self.reverse_proxy)
                    self.reverse_proxy_ip_address_header = application_config_json.get('reverse_proxy_ip_address_header', self.reverse_proxy_ip_address_header)

                    self.demo_mode = application_config_json.get('demomode', self.demo_mode)
                    if self.demo_mode:
                        self.event_batch_size_limit = 1
                        self.event_time_limit_seconds = 5

                    #for old tcell_input_url
                    self.company = application_config_json.get("company")

    def load_app_sensor_restrictions(self):
        self.blacklisted_params = {
                "token": True,
                "client_secret": True,
                "password": True,
                "passwd": True,
                "refresh_token": True,
                "pf.pass": True,
                "user.password": True }
        self.whitelisted_params = {}
        self.whitelist_present = False

        payloads_config_filename = os.environ.get("TCELL_AGENT_PAYLOADS_CONFIG", "tcell_agent_payloads.config")

        if os.path.isfile(payloads_config_filename) == True:
            try:
                with open(payloads_config_filename) as data_file:
                    payloads_config_json = yaml.safe_load(data_file)

                    if (payloads_config_json.get("blacklisted") is not None):
                        self.blacklisted_params = {}
                        for term in payloads_config_json["blacklisted"]:
                            self.blacklisted_params[term.lower()] = True

                    if (payloads_config_json.get("whitelisted") is not None):
                        self.whitelist_present = True

                        for term in payloads_config_json["whitelisted"]:
                            self.whitelisted_params[term.lower()] = True

            except Exception as e:
                self.allow_unencrypted_appsensor_payloads = False

                print(" ********* ********* ********* **********")
                print(" tCell.io                                ")
                print(" Could not load payloads config file     ")
                print(" ERROR:                                  ")
                print(e)
                print(" ********* ********* ********* **********")
