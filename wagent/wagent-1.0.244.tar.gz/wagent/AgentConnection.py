#! /usr/bin/env python

from subprocess import Popen
import os
import socket
import subprocess
import json
import sys
from os import path
import tempfile
from threading import Thread
from threading import Event


def __create_process(server_path, agent_path, timeout, debug):

    if debug:
        popen_params = ["php", "-f", server_path, agent_path, timeout, 'debug']
    else:
        popen_params = ["php", "-f", server_path, agent_path, timeout]

    p = Popen(popen_params,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    p.stdout.readline()

    if not debug:
        return

    while True:
        nextLine = p.stdout.readline()
        if nextLine is None or nextLine == '':
            break
        sys.stdout.write(nextLine)


def __start_server_process(server_path, agent_path, timeout, event, debug):
    __create_process(server_path, agent_path, timeout, debug)
    event.set()


def start_and_wait_server(agent_server, agent_path, timeout, debug):
    event = Event()
    thread = Thread(target=__start_server_process, args=(agent_server, agent_path, timeout, event, debug))
    thread.start()
    event.wait(5)


class AgentConnection:

    AUTOREPLY_NONE = 1
    AUTOREPLY_DELIVERED = 2
    AUTOREPLY_READ = 3

    def __getAgentPath(self, phoneNumber):
        agentpath = path.join (tempfile.gettempdir(), phoneNumber)
        if not os.path.exists(agentpath):
            os.makedirs(agentpath)
        return agentpath

    def __currentServer(self, serverSocket):
        conn = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        err = conn.connect_ex (serverSocket)
        if err != 0:
            conn.close ()
            return None
        return conn

    def __getParentDir (self,path):
        index = path.rfind (os.sep)
        if index == -1:
            return os.sep
        parent = path [:index - len(path)]
        return parent

    def __getServerPath (self):
        currentScriptDir = os.path.dirname(__file__)
        return os.path.join(currentScriptDir,'php','agent-server')

    def __startServer(self, agent_path, timeout, debug):
        agent_server = self.__getServerPath()
        start_and_wait_server(agent_server, agent_path, timeout, debug)

    def __getOrCreateConnection(self, phoneNumber, timeout, debug):
        agent_path = self.__getAgentPath(phoneNumber)
        serverSocket = path.join (agent_path, "server.sock")
        conn = None
        tries = 0
        while conn is None and tries < 3:
            conn = self.__currentServer (serverSocket)
            if conn is not None:
                return conn
            self.__startServer (agent_path, timeout, debug)
            tries = tries + 1
        return conn

    def __init__(self, phoneNumber, timeout = "120", debug = False):
        self.conn = self.__getOrCreateConnection (phoneNumber, timeout, debug)
        if self.conn is not None:
            self.fd = self.conn.makefile()

    def __WriteInt (self, data):
        self.__WriteLine(str(data))

    def __WriteBool (self, data):
        if not data:
            self.__WriteLine('0')
        else:
            self.__WriteLine('1')

    def __WriteLine (self, data):
        if data is None or (not data):
            line = '_none_a35825979c956e5a1f068e7cb21c280c'
        else:
            line = data.replace('\n', '\\n')
        buff = (line + '\n').encode('utf-8')
        self.conn.sendall (buff)

    def __WriteArray (self, array):

        if array is None:
            self.__WriteLine (None)
            return

        line = '|'.join (array)
        self.__WriteLine (line)

    def __ReadLine (self):
        data = self.__ReadLineEscaped ()
        if data == '_none_a35825979c956e5a1f068e7cb21c280c':
            return None
        return data.replace('\\n', '\n')

    def __ReadLineEscaped (self):
        data = self.fd.readline()
        return data.strip().decode ('utf-8')

    def __ReadObject (self):
        dataRaw = self.__ReadLineEscaped ()
        if not dataRaw or dataRaw.isspace():
            return {'code': '500', 'message': 'agent server communication failed'}
        return json.loads(dataRaw)

    def isLiteConnected (self):
        if self.conn is None:
            return False
        try:
            self.__WriteLine ('isliteconnected')
        except socket.error as e:
            self.conn.close()
            self.conn = None
            raise
        res = self.__ReadLine ()
        if res == "1":
            return True
        return False

    def isConnected (self):
        if self.conn is None:
            return False
        try:
            self.__WriteLine ('isconnected')
        except socket.error as e:
            self.conn.close()
            self.conn = None
            raise
        res = self.__ReadLine ()
        if res == "1":
            return True
        return False

    def isLoggedIn (self):
        if self.conn is None:
            return False
        self.__WriteLine ('isloggedin')
        res = self.__ReadLine ()
        if res == "1":
            return True
        return False

    def disconnect (self):
        if not (self.conn is None):
            self.conn.send('quit\r\n')
            self.conn.shutdown(socket.SHUT_RDWR)
            self.conn.close()
            self.conn = None

    def liteConnect (self, number, nickname, autoreply = AUTOREPLY_DELIVERED):
        self.__WriteLine ('liteconnect')
        self.__WriteLine (number)
        self.__WriteLine (nickname)
        self.__WriteInt (autoreply)
        return self.__ReadObject()

    def connect (self, number, nickname, autoreply = AUTOREPLY_DELIVERED):
        self.__WriteLine ('connect')
        self.__WriteLine (number)
        self.__WriteLine (nickname)
        self.__WriteInt (autoreply)
        return self.__ReadObject()

    def login (self, password):
        self.__WriteLine ('login')
        self.__WriteLine (password)
        return self.__ReadLine ()


    def __ReadEvent(self):
        name = self.__ReadLine ()
        if name == 'OK' or name == 'ERROR':
            return None
        data = self.__ReadObject ()
        return { "name": name, "data": data }

    def __peekEvents (self, peekEventName):
        events = []
        self.__WriteLine (peekEventName)
        event = self.__ReadEvent ()
        while not (event is None):
            data = event.get ('data')
            if data is not None and data.get('code') is not None and data.get('code') == '500':
                break
            events.append (event)
            event = self.__ReadEvent ()

        return events

    def peekEvents (self):
        return self.__peekEvents ('peekevents')

    def peekEventsForce (self):
        return self.__peekEvents ('peekeventsforce')

    def sendActiveStatus(self):
        self.__WriteLine ('sendactivestatus')
        result = self.__ReadLine()
        if result == 'OK':
            return {"code": "200"}
        return {"code":"500"}

    def sendOfflineStatus(self):
        self.__WriteLine ('sendofflinestatus')
        result = self.__ReadLine()
        if (result == 'OK'):
            return {"code":"200"}
        return {"code":"500"}

    def setConnectedStatus (self, status):
        if status == 'online':
            return self.sendActiveStatus()
        return self.sendOfflineStatus()

    def getConnectedStatus (self):
        self.__WriteLine ('getconnectedstatus')
        return self.__ReadObject ()

    def sendGetGroups(self):
        self.__WriteLine ('sendgetgroups')
        return self.__ReadObject ()

    def sendGetClientConfig(self):
        self.__WriteLine ('sendgetclientconfig')
        return self.__ReadObject ()

    def sendChangeNumber(self, number):
        self.__WriteLine ('sendchangenumber')
        self.__WriteLine (number)
        return self.__ReadObject ()

    def sendGetPrivacySettings(self):
        self.__WriteLine ('sendgetprivacysettings')
        return self.__ReadObject ()

    def sendSetPrivacySettings(self, category, value):
        self.__WriteLine ('sendsetprivacysettings')
        self.__WriteLine (category)
        self.__WriteLine (value)
        return self.__ReadObject ()

    def sendGetProfilePicture(self, number):
        self.__WriteLine ('sendgetprofilepicture')
        self.__WriteLine (number)
        self.__WriteLine ('large')
        return self.__ReadObject ()

    def sendGetProfilePicturePreview(self, number):
        self.__WriteLine ('sendgetprofilepicture')
        self.__WriteLine (number)
        self.__WriteLine ('preview')
        return self.__ReadObject ()

    def sendGetServerProperties(self):
        self.__WriteLine ('sendgetserverproperties')
        return self.__ReadObject ()

    def sendRemoveAccount(self, feedback):
        self.__WriteLine ('sendremoveaccount')
        self.__WriteLine ("")
        self.__WriteLine ("")
        self.__WriteLine (feedback)
        return self.__ReadObject()

    def sendGetStatuses(self, jids):
        self.__WriteLine ('sendgetstatuses')
        self.__WriteArray (jids)
        return self.__ReadObject ()

    def sendGroupsChatCreate(self, subject, participants):
        self.__WriteLine ('sendgroupschatcreate')
        self.__WriteLine (subject)
        self.__WriteArray (participants)
        return self.__ReadObject ()

    def sendSetGroupSubject(self, gjid, subject):
        self.__WriteLine ('sendsetgroupsubject')
        self.__WriteLine (gjid)
        self.__WriteLine (subject)
        return self.__ReadObject ()

    def sendGroupsLeave(self, gjid):
        self.__WriteLine ('sendgroupsleave')
        self.__WriteLine (gjid)
        return self.__ReadObject ()

    def sendGroupsParticipantAdd(self, gjid, participant):
        self.__WriteLine ('sendgroupsparticipantadd')
        self.__WriteLine (gjid)
        self.__WriteLine (participant)
        return self.__ReadObject ()

    def sendGroupsParticipantRemove(self, gjid, participant):
        self.__WriteLine ('sendgroupsparticipantremove')
        self.__WriteLine (gjid)
        self.__WriteLine (participant)
        return self.__ReadObject ()

    def sendPromoteParticipant(self, gjid, participant):
        self.__WriteLine ('sendpromoteparticipant')
        self.__WriteLine (gjid)
        self.__WriteLine (participant)
        return self.__ReadObject ()

    def sendDemoteParticipant(self, gjid, participant):
        self.__WriteLine ('senddemoteparticipant')
        self.__WriteLine (gjid)
        self.__WriteLine (participant)
        return self.__ReadObject ()

    def createMessageId (self):
        self.__WriteLine('createmessageid')
        return self.__ReadLine()

    def sendMessage(self, number, message, message_id = None):
        self.__WriteLine ('sendmessage')
        self.__WriteLine (number)
        self.__WriteLine (message)
        self.__WriteLine (message_id)
        return self.__ReadObject ()

    def sendMessageDelivered(self, to, msgid):
        self.__WriteLine ('sendmessagedelivered')
        self.__WriteLine (to)
        self.__WriteLine (msgid)
        result = self.__ReadLine()
        if (result == 'OK'):
            return {"code":"200"}
        return {"code":"500"}

    def sendMessageDeliveredBatch(self, to, msgids):
        self.__WriteLine ('sendmessagedeliveredbatch')
        self.__WriteLine (to)
        self.__WriteArray (msgids)
        result = self.__ReadLine()
        if (result == 'OK'):
            return {"code":"200"}
        return {"code":"500"}

    def sendMessageRead(self, to, msgid):
        self.__WriteLine ('sendmessageread')
        self.__WriteLine (to)
        self.__WriteLine (msgid)
        result = self.__ReadLine()
        if (result == 'OK'):
            return {"code":"200"}
        return {"code":"500"}

    def sendMessageReadBatch(self, to, msgids):
        self.__WriteLine ('sendmessagereadbatch')
        self.__WriteLine (to)
        self.__WriteArray (msgids)
        result = self.__ReadLine()
        if (result == 'OK'):
            return {"code":"200"}
        return {"code":"500"}

    def sendGroupMessageRead(self, to, msgid, participant):
        self.__WriteLine ('sendgroupmessageread')
        self.__WriteLine (to)
        self.__WriteLine (msgid)
        self.__WriteLine (participant)
        result = self.__ReadLine()
        if (result == 'OK'):
            return {"code":"200"}
        return {"code":"500"}

    def sendGroupMessageReadBatch(self, to, msgids, participant):
        self.__WriteLine ('sendgroupmessagereadbatch')
        self.__WriteLine (to)
        self.__WriteArray (msgids)
        self.__WriteLine (participant)
        result = self.__ReadLine()
        if (result == 'OK'):
            return {"code":"200"}
        return {"code":"500"}

    def sendGroupMessageDelivered(self, to, msgid, participant):
        self.__WriteLine ('sendgroupmessagedelivered')
        self.__WriteLine (to)
        self.__WriteLine (msgid)
        self.__WriteLine (participant)
        result = self.__ReadLine()
        if (result == 'OK'):
            return {"code":"200"}
        return {"code":"500"}

    def sendGroupMessageDeliveredBatch(self, to, msgids, participant):
        self.__WriteLine ('sendgroupmessagedeliveredbatch')
        self.__WriteLine (to)
        self.__WriteArray (msgids)
        self.__WriteLine (participant)
        result = self.__ReadLine()
        if (result == 'OK'):
            return {"code":"200"}
        return {"code":"500"}

    def sendMessageAudio(self, to, imageURL, voice = False, msgid = None, storeURLmedia = False, file_size = 0, file_hash = ''):
        self.__WriteLine ('sendmessageaudio')
        self.__WriteLine (to)
        self.__WriteLine (imageURL)
        self.__WriteBool (voice)
        self.__WriteLine (msgid)
        self.__WriteBool (storeURLmedia)
        self.__WriteInt (file_size)
        self.__WriteLine (file_hash)
        return self.__ReadObject ()

    def sendMessageComposing(self, to):
        self.__WriteLine ('sendmessagecomposing')
        self.__WriteLine (to)
        result = self.__ReadLine()
        if (result == 'OK'):
            return {"code":"200"}
        return {"code":"500"}

    def sendMessagePaused(self, to):
        self.__WriteLine ('sendmessagepaused')
        self.__WriteLine (to)
        result = self.__ReadLine()
        if (result == 'OK'):
            return {"code":"200"}
        return {"code":"500"}

    def sendMessageImage(self, to, imageURL, caption = '', message_id = None, storeURLmedia = False, file_size = 0, file_hash = None):
        self.__WriteLine ('sendmessageimage')
        self.__WriteLine (to)
        self.__WriteLine (imageURL)
        self.__WriteLine (caption)
        self.__WriteLine (message_id)
        self.__WriteBool (storeURLmedia)
        self.__WriteInt (file_size)
        self.__WriteLine (file_hash)
        return self.__ReadObject ()


    def sendMessageLocation(self, to,latitude ,longitude, name = '', url = None, message_id = None):
        self.__WriteLine ('sendmessagelocation')
        self.__WriteLine (to)
        self.__WriteLine (latitude)
        self.__WriteLine (longitude)
        self.__WriteLine (name)
        self.__WriteLine (url)
        self.__WriteLine (message_id)
        return self.__ReadObject ()


    def sendMessageVideo(self, to, imageURL, caption = '', message_id = None, storeURLmedia = False, file_size = 0, file_hash = None):
        self.__WriteLine ('sendmessagevideo')
        self.__WriteLine (to)
        self.__WriteLine (imageURL)
        self.__WriteLine (caption)
        self.__WriteLine (message_id)
        self.__WriteBool (storeURLmedia)
        self.__WriteInt (file_size)
        self.__WriteLine (file_hash)
        return self.__ReadObject ()

    def sendUpdateNickname(self, nickname):
        self.__WriteLine ('sendupdatenickname')
        self.__WriteLine (nickname)
        result = self.__ReadLine()
        if (result == 'OK'):
            return {"code":"200"}
        return {"code":"500"}

    def sendGetPresences(self, to):
        self.__WriteLine ('sendgetpresences')
        self.__WriteArray (to)
        return self.__ReadObject ()

    def sendGetPrivacyBlockedList(self):
        self.__WriteLine('sendgetprivacyblockedlist')
        return self.__ReadObject()

    def sendSetPrivacyBlockedList(self, blockedJids):
        self.__WriteLine ('sendsetprivacyblockedlist')
        self.__WriteArray (blockedJids)
        result = self.__ReadLine()
        if (result == 'OK'):
            return {"code":"200"}
        return {"code":"500"}

    def sendSetProfilePicture(self, path):
        self.__WriteLine ('sendsetprofilepicture')
        self.__WriteLine (path)
        return self.__ReadObject ()

    def sendRemoveProfilePicture(self):
        self.__WriteLine ('sendremoveprofilepicture')
        return self.__ReadObject ()

    def sendStatusUpdate(self, text):
        self.__WriteLine ('sendstatusupdate')
        self.__WriteLine (text)
        return self.__ReadObject()

    def sendVcard(self, to, vCard, name = '', message_id = None):
        self.__WriteLine ('sendvcard')
        self.__WriteLine (to)
        self.__WriteLine (vCard)
        self.__WriteLine (name)
        self.__WriteLine (message_id)
        return self.__ReadObject ()

    def sendSync(self, numbers, deleted = None, sync_type = 3):
        self.__WriteLine ('sendsync')
        self.__WriteArray (numbers)
        self.__WriteArray (deleted)
        self.__WriteInt (sync_type)
        return self.__ReadObject ()

    def checkCredentials(self):
        self.__WriteLine ('checkcredentials')
        return self.__ReadObject ()

    def codeRegister(self, code):
        self.__WriteLine ('coderegister')
        self.__WriteLine (code)
        return self.__ReadObject ()

    def codeRequestSMS(self):
        self.__WriteLine ('coderequest')
        self.__WriteLine ('sms')
        return self.__ReadObject ()

    def codeRequestVoice(self):
        self.__WriteLine ('coderequest')
        self.__WriteLine ('voice')
        return self.__ReadObject ()
