# -*- coding: utf-8 -*-
##############################################################################
#
#    pyFlyDoc, python library for FlyDoc webservices
#    Copyright (C) 2014 SYLEAM Info Services (<http://www.Syleam.fr/>)
#              Sylvain Garancher <sylvain.garancher@syleam.fr>
#
#    This file is a part of pyFlyDoc
#
#    pyFlyDoc is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    pyFlyDoc is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import os
import base64
import pkg_resources
from enum import Enum, IntEnum
from suds.client import Client


class FlyDocTransportName(Enum):
    Archive = 'Archive'
    CmdLine = 'Command line'
    Pickup = 'Delivery Warerule'
    Mail = 'Email'
    Fax = 'Fax'
    CustomData = 'Flexible form'
    GARC = 'Generic archive'
    MODEsker = 'Mail'
    Sms = 'SMS'
    UserForm = 'User form'
    FaxRecv = 'Received Fax'


class FlyDocTransportState(IntEnum):
    Queued = 0
    Submitted = 10
    Accepted = 30
    Converting = 40
    Ready = 50
    OnRetry = 60
    Hold = 70
    Busy = 80
    Waiting = 90
    Successful = 100
    Failure = 200
    Canceled = 300
    Rejected = 400


class FlyDocService(object):
    """
    Base for FlyDoc services classes
    Loads the WSDL file at instanciation and defines some helpers to simplify written code
    """
    def __init__(self, wsdlFile):
        self.client = Client(wsdlFile)

    def _create(self, name, values=None):
        """
        Creates, and optioally populates, a new complex type instance
        """
        if values is None:
            values = {}

        value = self.client.factory.create(name)
        for key, val in values.items():
            value[key] = val

        return value

    def _getLastResponseHeaders(self):
        """
        Returns the headers of the last received response
        """
        return self.client.last_received().getChild('Envelope').getChild('Header')

    def _addHeader(self, headerName, headerValue):
        """
        Add a header for the soap query
        """
        headers = self.client.options.soapheaders
        if not isinstance(headers, dict):
            headers = {}
        headers.update({headerName: headerValue})
        self.client.set_options(soapheaders=headers)

    def __getattr__(self, name):
        """
        Binds method calls on the class, and all other calls prefixed by an underscore
        """
        if name.startswith('_') and hasattr(self.client, name[1:]):
            return getattr(self.client, name[1:])

        if hasattr(self.client.service, name):
            return getattr(self.client.service, name)

        raise AttributeError('Unknown attribute %s' % name)


class FlyDocSessionService(FlyDocService):
    """
    Session Service class
    """
    def __init__(self, wsdlFile=None):
        if wsdlFile is None:
            wsdlFile = 'file://' + pkg_resources.resource_filename('pyflydoc', 'WSDL/SessionService.wsdl')

        super(FlyDocSessionService, self).__init__(wsdlFile)


class FlyDocSubmissionService(FlyDocService):
    """
    Submission Service class
    """
    def __init__(self, wsdlFile=None):
        if wsdlFile is None:
            wsdlFile = 'file://' + pkg_resources.resource_filename('pyflydoc', 'WSDL/SubmissionService.wsdl')

        super(FlyDocSubmissionService, self).__init__(wsdlFile)

        # Initialize enumeration constants
        self.ATTACHMENTS_FILTER = self.client.factory.create('ATTACHMENTS_FILTER')
        self.RESOURCE_TYPE = self.client.factory.create('RESOURCE_TYPE')
        self.WSFILE_MODE = self.client.factory.create('WSFILE_MODE')
        self.VAR_TYPE = self.client.factory.create('VAR_TYPE')

    def _readFile(self, attachment):
        """
        Creates a WSFile object, with contents of the supplied attachment file
        @param attachment : Name of the file to read
        """
        wsFile = self._create('WSFile')
        wsFile.name = os.path.basename(attachment)
        wsFile.mode = self.WSFILE_MODE.MODE_INLINED
        with open(attachment, 'r') as fil:
            wsFile.content = base64.b64encode(fil.read())

        return wsFile

    def _createFile(self, name, data):
        """
        Creates a WSFile object, with data supplied as argument
        @param name : Name of the created WSFile
        @param data : Data to put in the WSFile
        """
        wsFile = self._create('WSFile')
        wsFile.name = name
        wsFile.mode = self.WSFILE_MODE.MODE_INLINED
        wsFile.content = base64.b64encode(data)
        return wsFile


class FlyDocQueryService(FlyDocService):
    """
    Query Service class
    """
    def __init__(self, wsdlFile=None):
        if wsdlFile is None:
            wsdlFile = 'file://' + pkg_resources.resource_filename('pyflydoc', 'WSDL/QueryService.wsdl')

        super(FlyDocQueryService, self).__init__(wsdlFile)

        # Initialize enumeration constants
        self.ATTACHMENTS_FILTER = self.client.factory.create('ATTACHMENTS_FILTER')
        self.WSFILE_MODE = self.client.factory.create('WSFILE_MODE')
        self.VAR_TYPE = self.client.factory.create('VAR_TYPE')


class FlyDoc(object):
    """
    General FlyDoc class
    """
    def __init__(self, sessionServiceWsdlFile=None, submissionServiceWsdlFile=None, queryServiceWsdlFile=None):
        """
        Initialize services instances from WSDL files
        """
        self.sessionService = FlyDocSessionService(sessionServiceWsdlFile)
        self.submissionService = FlyDocSubmissionService(submissionServiceWsdlFile)
        self.queryService = FlyDocQueryService(queryServiceWsdlFile)

    def login(self, username, password):
        """
        Initialize the services by retrieving a session identifier
        """
        # Initialize services bindings
        bindings = self.sessionService.GetBindings(username)
        self.sessionService._set_options(location=str(bindings.sessionServiceLocation))
        self.submissionService._set_options(location=str(bindings.submissionServiceLocation))
        self.queryService._set_options(location=str(bindings.queryServiceLocation))

        # Call the login method
        self.loginInfo = self.sessionService.Login(userName=username, password=password)

        # Define the session header value
        SessionHeaderValue = self.sessionService._create('SessionHeader')
        SessionHeaderValue.sessionID = self.loginInfo.sessionID

        # Set the proper header values
        self.sessionService._addHeader('SessionHeaderValue', SessionHeaderValue)
        self.submissionService._addHeader('SessionHeaderValue', SessionHeaderValue)
        self.queryService._addHeader('SessionHeaderValue', SessionHeaderValue)

    def logout(self):
        """
        Close the connection with the services
        """
        self.sessionService.Logout()

    def submit(self, name, transportVars, transportAttachments=None, transportContents=None):
        """
        Send some documents to FlyDoc
        """
        if transportAttachments is None:
            transportAttachments = []

        if transportContents is None:
            transportContents = {}

        # Create a new transport
        transport = self.submissionService._create('Transport')
        transport.transportName = name

        # Add vars in the transport
        transport.vars.Var.extend([self.submissionService._create('Var', {
            'attribute': attribute,
            'simpleValue': value,
            'type': self.submissionService.VAR_TYPE.TYPE_STRING,
        }) for attribute, value in transportVars.items()])

        # Add files in attachments
        transport.attachments.Attachment.extend([self.submissionService._create('Attachment', {
            'sourceAttachment': self.submissionService._readFile(attachment),
        }) for attachment in transportAttachments])
        # Add direct contents in attachments
        transport.attachments.Attachment.extend([self.submissionService._create('Attachment', {
            'sourceAttachment': self.submissionService._createFile(content['name'], content['data'])
        }) for content in transportContents])

        # Submit the transport
        return self.submissionService.SubmitTransport(transport=transport)

    def browse(self, filter='msn=*', sortOrder='', attributes='', nItems=None, includeSubNodes=False, searchInArchive=False, reverse=False):
        """
        Generator used to browse transports
        """
        # Create QueryRequest object
        request = self.queryService._create('QueryRequest')
        # Request for transports one by one for the generator to work
        request.nItems = 1
        request.filter = filter
        request.sortOrder = sortOrder
        request.attributes = attributes
        request.includeSubNodes = includeSubNodes
        request.searchInArchive = searchInArchive

        # Request for the first or last item, depending on the order
        if not reverse:
            result = self.queryService.QueryFirst(request)
        else:
            result = self.queryService.QueryLast(request)

        totalNumber = result.nTransports
        # Check if there is at least one result
        if result.nTransports > 0:
            yield result.transports.Transport[0]

        # Add the queryID in headers (required)
        QueryHeaderValue = self.queryService._create('QueryHeader')
        QueryHeaderValue.queryID = self.queryService._getLastResponseHeaders().getChild('QueryHeaderValue').getChild('queryID').getText()
        self.queryService._addHeader('QueryHeaderValue', QueryHeaderValue)
        while(not result.noMoreItems and (nItems is not None and totalNumber < nItems)):
            # Request for the next item, depending on the order
            if not reverse:
                result = self.queryService.QueryNext(request)
            else:
                result = self.queryService.QueryPrevious(request)

            totalNumber += result.nTransports
            if result.nTransports > 0:
                yield result.transports.Transport[0]

    def browseAttachments(self, transportID, attachmentFilter=None, outputFileMode=None):
        """
        Generator used to browse attachments of a transport
        """
        for attachment in self.queryService.QueryAttachments(transportID, attachmentFilter, outputFileMode).attachments.Attachment:
            yield attachment

    def approve(self, identifier):
        """
        Approve a transport that is waiting for validation
        The identifier argument can be an integer (transportID), or a complex filter (QueryRequest)
        """
        return self.queryService.Approve(identifier)

    def cancel(self, identifier):
        """
        Cancel a transport that is waiting for validation
        The identifier argument can be an integer (transportID), or a complex filter (QueryRequest)
        """
        return self.queryService.Cancel(identifier)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
