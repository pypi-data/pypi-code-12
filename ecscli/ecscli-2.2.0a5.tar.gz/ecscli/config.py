#!/usr/bin/python
# Copyright (c)2012 EMC Corporation
# All Rights Reserved

# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.

import json
import common
import glob
import os
import sys
from sys import version_info
from common import SOSError
from os.path import expanduser


from common import SOSError


class Config(object):
    CONFIG_BASE_NAME      = "ecscliconfig_"
    #CONFIG_PATH           = os.path.dirname(__file__)
    CONFIG_PATH           = expanduser("~")
    CONFIG_BASE_NAME_PATH = CONFIG_PATH + "/" + CONFIG_BASE_NAME
    CONFIG_CURRENT        = CONFIG_PATH + "/." + CONFIG_BASE_NAME + ".json"

    HOSTNAME = "hostname"
    PORT = "port"
    USER = "user"
    COOKIEDIR = "cookiedir" #defaults to Config.CONFIG_PATH + '/' + args.profile where args.profile is the name of the config

    def __init__(self):
        return


##################################################################
# convenience method not sure if it will be used
##################################################################
def getActiveConfigName():
    activeConfigName = ""

    configArr = glob.glob(Config.CONFIG_BASE_NAME_PATH + '*')
    output = "Getting active config profile name: "
    for configItem in configArr:
        fn_and_path = configItem.split('/')
        fn = fn_and_path[-1]
        profNameArr = fn.split('_')
        profName = profNameArr[1]
        if (os.readlink(Config.CONFIG_CURRENT) == configItem):
            activeConfigName = profName
            output += profName
            break
    return activeConfigName


##################################################################
#
##################################################################
def loadConfig(profileName):
    profileFile = Config.CONFIG_BASE_NAME_PATH + profileName + "_.json"
    in_file = open(profileFile,"r")
    result = json.load(in_file)
    in_file.close()
    return result

##################################################################
# internally used to load these default values for other cli commands
##################################################################
def loadCurrentConfig():
    if os.path.exists(Config.CONFIG_CURRENT) == False:
        return None

    in_file = open(Config.CONFIG_CURRENT,"r")
    result = json.load(in_file)
    in_file.close()
    return result


##################################################################
# 
##################################################################
def saveConfig(data , profileName):
    print("Entered saveConfig profileName = " + profileName)
    print("will be saved to base path: " + Config.CONFIG_BASE_NAME_PATH)
    profileFile = Config.CONFIG_BASE_NAME_PATH + profileName + "_.json"
    print("Saving profile config to: " + profileFile)
    out_file = open(profileFile,"w")
    json.dump(data, out_file, indent=4)
    out_file.close()
    try:
        os.symlink(profileFile, Config.CONFIG_CURRENT)
    except:
        os.remove(Config.CONFIG_CURRENT)
        os.symlink(profileFile, Config.CONFIG_CURRENT)
    return

##################################################################
#
##################################################################
def promptUser(promptStr):
    py3 = version_info[0] > 2 #creates boolean value for test that Python major version > 2
    if py3:
        response = input(promptStr)
    else:
        response = raw_input(promptStr)
    return response

##################################################################
#
##################################################################
def configFileFromName(profileName):
    return Config.CONFIG_BASE_NAME_PATH + profileName + "_.json"

##################################################################
#
##################################################################
def isProfileCurrent(profileName):
    status = False
    profileFile = configFileFromName(profileName)

    if os.path.exists(Config.CONFIG_CURRENT):
        if (os.readlink(Config.CONFIG_CURRENT) == profileFile):
            status = True
    return status
    



########################################################
#
# parser commands section
#
#########################################################
def cli_config_del_parser(subcommand_parsers):
    # create namespace command parser
    cli_config_del_parser = subcommand_parsers.add_parser(
        'delete',
        description='deletes a saved configuration profile from the profile list',
        conflict_handler='resolve',
        help='del a cli profile')

    cli_config_del_parser.add_argument(
        '-pf', '-profile',
        help='the name of the profile whose values will be the host, username, cookiefile and port',
        dest='profile',
        required=True)

    cli_config_del_parser.set_defaults(func=deleteProfile)

##################################################################
#
##################################################################
def deleteProfile(args):
    currentRemoved = False
    profileFile = configFileFromName(args.profile)
   
    #check on the current profile sym link and remove it if it points to this one
    if (os.readlink(Config.CONFIG_CURRENT) == profileFile):
        os.remove(Config.CONFIG_CURRENT)
        currentRemoved = True
   
    #delete the json config file with this profile name
    os.remove(profileFile)

    # if there are any current configs left and the current config was the one that was removed
    # then update current config to the first one in the list of configs
    configArr = glob.glob(Config.CONFIG_BASE_NAME_PATH + '*')
    if ((currentRemoved == True) and (len(configArr)>0 )):
        os.symlink(configArr[0], Config.CONFIG_CURRENT)

    listConfigs()
    return


##################################################################
#
##################################################################
def cli_config_list_parser(subcommand_parsers):
    # create namespace command parser
    cli_config_list_parser = subcommand_parsers.add_parser(
        'list',
        description='list the available cli configuration profiles',
        conflict_handler='resolve',
        help='list cli profiles')
    cli_config_list_parser.set_defaults(func=listConfigs)


##################################################################
#
##################################################################
def listConfigs(args = None):
    configArr = glob.glob(Config.CONFIG_BASE_NAME_PATH + '*')
    print("list of existing configuration profiles: ")
    for configItem in configArr:
        fn_and_path = configItem.split('/')
        fn = fn_and_path[-1]
        profNameArr = fn.split('_')
        profName = profNameArr[1]
        line = "\t"
        if (os.readlink(Config.CONFIG_CURRENT) == configItem):
            line += "* "
        else:
            line += "  "
        line += profName
        #TODO load the profile to add some details here
        c = loadConfig(profName)
        line += " -  \thostname:" + c[Config.HOSTNAME] + ":" + c[Config.PORT] + "\t\tuser:" + c[Config.USER]
        print(line)
    return 

##################################################################
#
##################################################################
def config_set_active_parser(subcommand_parsers):
    # create namespace command parser
    parser = subcommand_parsers.add_parser(
        'set',
        description='sets the active cli configuration profile',
        conflict_handler='resolve',
        help='list cli profiles')

    parser.add_argument(
        '-pf', '-profile',
        help='the name of the profile whose values will be the host, username, cookiefile and port',
        dest='profile',
        required=True)

    parser.set_defaults(func=setActiveConfig)

##################################################################
#
##################################################################
def setActiveConfig(args):
    profileFile = Config.CONFIG_BASE_NAME_PATH + args.profile + "_.json"
    try:
        os.symlink(profileFile, Config.CONFIG_CURRENT)
    except:
        os.remove(Config.CONFIG_CURRENT)
        os.symlink(profileFile, Config.CONFIG_CURRENT)

    listConfigs()
    return

##################################################################
#
##################################################################
def cli_config_parser(parent_subparser):
    subcommand_list = ['-h', '--help', 'list', 'set', 'delete']
    cli_config_parser = parent_subparser.add_parser(
        'config',
        description='ECS profile configuration to set default values for host, user, cookiefile and port. To create a profile no subcommand is needed just use "ecscli config" and you will be prompted for information, but you may optionally enter a profile name with the -pf/-profile arg',
        conflict_handler='resolve',
        help='ecscli profile configuration')
    cli_config_parser.add_argument(
        '-pf', '-profile',
        help='multiple profiles can be saved. If a profile name is not given, the prompted username value will be used',
        dest='profile')

    if sys.argv[1] == "config":
        if len(sys.argv) > 2 and (sys.argv[2] in subcommand_list):
            subcommand_parsers = cli_config_parser.add_subparsers(help='Use One Of Commands')
            cli_config_list_parser(subcommand_parsers)
            config_set_active_parser(subcommand_parsers)
            cli_config_del_parser(subcommand_parsers)
        else:
            cli_config_parser.set_defaults(func=createConfig)

##################################################################
#
##################################################################
def createConfig(args):
    h = promptUser("Please enter the default ECS hostname or ip (127.0.0.1):")
    if (h == ''):
        h = '127.0.0.1'
    p = promptUser("Please enter the default command port (4443):")
    if (p == ''):
        p = '4443'
    u = promptUser("Please enter the default user for the profile (root):")
    if (u == ''):
        u = 'root'
    if (args.profile is None):
        args.profile = u

    '''
    d = promptUser("Please enter a directory to save cookiefiles (" +   + "):)
    if (d ==''):
        d = Config.CONFIG_PATH + '/' + args.profile
    '''
    d = Config.CONFIG_PATH + '/' + args.profile


    theCfg = {}
    theCfg[Config.HOSTNAME] = h
    theCfg[Config.PORT] = p
    theCfg[Config.USER] = u
    theCfg[Config.COOKIEDIR] = d
    
    saveConfig(theCfg, args.profile)

    listConfigs()
    return

