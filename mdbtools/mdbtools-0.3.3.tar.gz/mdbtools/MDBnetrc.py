#!/usr/bin/env python
# encoding: utf-8

# Front Matter {{{
'''
Copyright (c) 2016 The Broad Institute, Inc.  All rights are reserved.

MDBnetrc.py: this file is part of mdbtools.  See the <root>/COPYRIGHT
file for the SOFTWARE COPYRIGHT and WARRANTY NOTICE.

@author: Michael S. Noble, David I. Heiman, Daniel DiCara
@date:   Mar 04, 2016

Most of this code was excerpted from the Broad TCGA GDOPS software suite:
    - GdacNetrc class written by David I. Heiman
    - CommonFunctions.confirm written by Daniel DiCara
It wraps the Python netrc with an interactive prompt (thus the inetrc name),
but will only prompt if being executed at a interactive terminal.
'''
# }}}

import os
import sys
import netrc
import readline
import getpass

class MDBnetrc(netrc.netrc):
    '''
    Extension to netrc that prompts the user for authentication information if
    the specified host isn't found in the .netrc file, then gives the user the
    option to update said file with the information entered.  However, the 
    prompt is only issued when running at an interactive terminal.
    '''

    def __init__(self, file=None):
        '''
        Constructor
        '''
        netrc.netrc.__init__(self, file)
        
        # Need to do this to add file to self, even though the same join was run
        # in netrc.netrc.__init__. This ensures compatibility with all 2.7.X
        # python versions. No need for try/except as it has already succeeded.
        if file is None:
            file = os.path.join(os.environ['HOME'], ".netrc")

        self.file = file
    
    def authenticators(self, host):
        '''
        Return a (user, account, password) tuple for given host.
        '''
        authentication = netrc.netrc.authenticators(self, host)
        if authentication is None:
            print "No authentication information found for %s in %s." % (host, self.file)
            if sys.stdout.isatty():
                authentication = self.ext_authentication(host)
        return authentication
    
    def ext_authentication(self, host):
        '''
        Prompt user for authentication information and return a
        (user, account, password) tuple for given host.
        '''        
        default_login = getpass.getuser()
        print "%s:" % host
        login = raw_input("\tLogin (%s): " % default_login)
        if not login.rstrip():
            login = default_login
        account = raw_input("\tAccount (None): ")
        if not account.rstrip():
            account = None
        password = getpass.getpass("\tPassword: ")
        authentication = (login, account, password)
        if self.confirm("Add %s to %s" % (host, self.file)):
            self.add_authentication(host, authentication)
        return authentication
    
    def add_authentication(self, host, authentication):
        '''
        Add new authentication credentials to list of hosts and update .netrc.
        '''
        self.hosts[host] = authentication
        auth_str = "machine %s login %s" % (host, authentication[0])
        if authentication[1] is not None:
            auth_str += " account %s" % authentication[1]
        auth_str += " password %s\n" % authentication[2]
        with open(self.file, 'a') as fp:
            fp.write(auth_str)

    def confirm(prompt=None):
        '''Confirmation prompt.  Returns True/False depending on user's choice.'''
        options = ['y','n','yes','no']
        option_string = '|'.join(options)
        if prompt is None:
            prompt = 'Enter %s: ' % option_string
        else:
            prompt = prompt + "? (%s) " % option_string
        while True:
            choice = raw_input(prompt).lower()
            if choice in options:
                return choice in {'y', 'yes'}
            else:
                print 'Invalid choice: %s' % choice

