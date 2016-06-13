#! /usr/bin/env python
# -*- coding: utf-8 -*-

import AgentConnection
import AgentException
import socket


class WinduAgent:
    AUTOREPLY_NONE = 1
    AUTOREPLY_DELIVERED = 2
    AUTOREPLY_READ = 3

    def __init__(self, phoneNumber, nickName = '', password='', autoReply=AUTOREPLY_NONE, timeout = 120, debug = False):
        self.phoneNumber = phoneNumber
        self.nickName = nickName
        self.autoReply = autoReply
        self.password = password
        self.conn = None
        self.timeout = timeout
        self.debug = debug

    def disconnect(self):
        if self.conn is not None:
            self.conn.disconnect()
            self.conn = None

    def __liteConnect(self):
        return self.conn.liteConnect(self.phoneNumber, self.nickName, self.autoReply)

    def __connect(self):
        return self.conn.connect(self.phoneNumber, self.nickName, self.autoReply)

    def __login(self):
        tries = 0
        while tries < 2:
            res = self.conn.login(self.password)
            if res == 'OK':
                return True
            tries += 1
        raise AgentException.AgentException("Login failed")

    def __ensureLiteConnected(self):
        tries = 0
        result = None
        while tries < 2:
            if self.conn is None:
                self.conn = AgentConnection.AgentConnection(self.phoneNumber, str(self.timeout), self.debug)
            try:
                if self.conn.isLiteConnected():
                    return
                result = self.__liteConnect()
            except socket.error as e:
                self.conn = None
            tries += 1

        if not self.conn.isLiteConnected():
            message = ''
            if result is not None and result.get('error') is not None:
                message = result.get('error')
            self.disconnect()
            raise AgentException.AgentException("Fail connecting to agent_server(" + message + ")")

    def __ensureConnected(self):
        tries = 0
        result = None
        while tries < 2:
            if self.conn is None:
                self.conn = AgentConnection.AgentConnection(self.phoneNumber, str(self.timeout), self.debug)
            try:
                if self.conn.isConnected():
                    return
                result = self.__connect()
            except socket.error as e:
                self.conn = None
            tries += 1

        if self.conn is None or not self.conn.isConnected():
            message = ''
            if result is not None and result.get('error') is not None:
                message = result.get('error')
            self.disconnect()
            raise AgentException.AgentException("Fail connecting to agent_server(" + message + ")")

    def __ensureLoggedIn(self):
        if not self.conn.isLoggedIn():
            self.__login()

    def __isConnected(self):
        if self.conn is None:
            return False
        return self.conn.isConnected()

    def isLoggedIn(self):
        if not self.__isConnected():
            return False
        return self.conn.isLoggedIn()

    def __connection(self):
        self.__ensureConnected()
        self.__ensureLoggedIn()
        return self.conn

    def __liteConnection(self):
        self.__ensureLiteConnected()
        return self.conn

    def peekEventsForce(self):
        conn = self.__connection()
        return conn.peekEventsForce()

    def peekEvents(self):
        conn = self.__connection()
        return conn.peekEvents()

    def ensureLoggedIn(self):
        return not (self.__connection() is None)

    def sendActiveStatus(self):
        conn = self.__connection()
        return conn.sendActiveStatus()

    def sendOfflineStatus(self):
        conn = self.__connection()
        return conn.sendOfflineStatus()

    def setConnectedStatus (self, status):
        conn = self.__connection()
        return conn.setConnectedStatus (status)

    def getConnectedStatus(self):
        conn = self.__connection()
        return conn.getConnectedStatus()

    def sendGetGroups(self):
        conn = self.__connection()
        return conn.sendGetGroups()

    def sendGetClientConfig(self):
        conn = self.__connection()
        return conn.sendGetClientConfig()

    def sendChangeNumber(self, number):
        conn = self.__connection()
        return conn.sendChangeNumber(number)

    def sendGetGroupV2Info(self, groupId):
        conn = self.__connection()
        return conn.sendGetGroupV2Info(groupId)

    def sendGetPrivacySettings(self):
        conn = self.__connection()
        return conn.sendGetPrivacySettings()

    def sendSetPrivacySettings(self, category, value):
        conn = self.__connection()
        return conn.sendSetPrivacySettings(category, value)

    def sendGetProfilePicture(self, number):
        conn = self.__connection()
        return conn.sendGetProfilePicture(number)

    def sendGetProfilePicturePreview(self, number):
        conn = self.__connection()
        return conn.sendGetProfilePicturePreview(number)

    def sendGetServerProperties(self):
        conn = self.__connection()
        return conn.sendGetServerProperties()

    def sendRemoveAccount(self, feedback):
        conn = self.__connection()
        return conn.sendRemoveAccount( feedback)

    def sendGetStatuses(self, jids):
        conn = self.__connection()
        return conn.sendGetStatuses(jids)

    def sendGroupsChatCreate(self, subject, participants):
        conn = self.__connection()
        return conn.sendGroupsChatCreate(subject, participants)

    def sendSetGroupSubject(self, gjid, subject):
        conn = self.__connection()
        return conn.sendSetGroupSubject(gjid, subject)

    def sendGroupsLeave(self, gjid):
        conn = self.__connection()
        return conn.sendGroupsLeave(gjid)

    def sendGroupsParticipantAdd(self, gjid, participant):
        conn = self.__connection()
        return conn.sendGroupsParticipantAdd(gjid, participant)

    def sendGroupsParticipantRemove(self, gjid, participant):
        conn = self.__connection()
        return conn.sendGroupsParticipantRemove(gjid, participant)

    def sendPromoteParticipant(self, gjid, participant):
        conn = self.__connection()
        return conn.sendPromoteParticipant(gjid, participant)

    def sendDemoteParticipant(self, gjid, participant):
        conn = self.__connection()
        return conn.sendDemoteParticipant(gjid, participant)

    def createMessageId(self):
        conn = self.__connection()
        return conn.createMessageId()

    def sendMessage(self, number, message, messageId = None):
        conn = self.__connection()
        return conn.sendMessage(number, message, messageId)

    def sendMessageDelivered(self, to, msgid):
        conn = self.__connection()
        return conn.sendMessageDelivered(to, msgid)

    def sendMessageDeliveredBatch(self, to, msgids):
        conn = self.__connection()
        return conn.sendMessageDeliveredBatch(to, msgids)

    def sendMessageRead(self, to, msgid):
        conn = self.__connection()
        return conn.sendMessageRead(to, msgid)

    def sendMessageReadBatch(self, to, msgids):
        conn = self.__connection()
        return conn.sendMessageReadBatch(to, msgids)

    def sendGroupMessageRead(self, to, msgid, participant):
        conn = self.__connection()
        return conn.sendGroupMessageRead(to, msgid, participant)

    def sendGroupMessageReadBatch(self, to, msgids, participant):
        conn = self.__connection()
        return conn.sendGroupMessageReadBatch(to, msgids, participant)

    def sendGroupMessageDelivered(self, to, msgid, participant):
        conn = self.__connection()
        return conn.sendGroupMessageDelivered(to, msgid, participant)

    def sendGroupMessageDeliveredBatch(self, to, msgids, participant):
        conn = self.__connection()
        return conn.sendGroupMessageDeliveredBatch(to, msgids, participant)

    def sendMessageAudio(self, to, file_path, voice = False, msgid = None, storeURLmedia = False, file_size = 0, file_hash = ''):
        conn = self.__connection()
        return conn.sendMessageAudio(to, file_path, voice , msgid , storeURLmedia , file_size, file_hash)

    def sendMessageComposing(self, to):
        conn = self.__connection()
        return conn.sendMessageComposing(to)

    def sendMessagePaused(self, to):
        conn = self.__connection()
        return conn.sendMessagePaused(to)

    def sendMessageImage(self, to, imageURL, caption = '', message_id = None, storeURLmedia = False, fsize = 0, fhash = None):
        conn = self.__connection()
        return conn.sendMessageImage(to, imageURL, caption, message_id, storeURLmedia, fsize, fhash)

    def sendMessageLocation(self, to, latitude, longitude , name = '', url = None, message_id = None):
        conn = self.__connection()
        return conn.sendMessageLocation(to, latitude, longitude, name, url, message_id)

    def sendMessageVideo(self, to, file_path, caption = '', message_id = None, storeURLmedia = False, file_size = 0, file_hash = None):
        conn = self.__connection()
        return conn.sendMessageVideo(to, file_path, caption, message_id, storeURLmedia, file_size, file_hash)

    def sendUpdateNickname(self, nickname):
        # if we didn't connect yet, just change the current nickName value.
        if not self.__isConnected():
            self.nickName = nickname
            return {"code":"200"}
        conn = self.__connection()
        return conn.sendUpdateNickname(nickname)

    def sendGetPresences(self, to):
        conn = self.__connection()
        return conn.sendGetPresences(to)

    def sendSetPrivacyBlockedList(self, blockedJids):
        conn = self.__connection()
        return conn.sendSetPrivacyBlockedList(blockedJids)

    def sendGetPrivacyBlockedList(self):
        conn = self.__connection()
        return conn.sendGetPrivacyBlockedList()

    def sendSetProfilePicture(self, path):
        conn = self.__connection()
        return conn.sendSetProfilePicture(path)

    def sendRemoveProfilePicture(self):
        conn = self.__connection()
        return conn.sendRemoveProfilePicture()

    def sendStatusUpdate(self, text):
        conn = self.__connection()
        return conn.sendStatusUpdate(text)

    def sendVcard(self, to, vCard, name ='',  message_id = None):
        conn = self.__connection()
        return conn.sendVcard(to, vCard, name , message_id)

    def sendSync(self, numbers, deleted = None, sync_type = 3):
        conn = self.__connection()
        return conn.sendSync(numbers, deleted, sync_type)

    def checkCredentials(self):
        conn = self.__liteConnection()
        return conn.checkCredentials()

    def codeRegister(self, code):
        conn = self.__liteConnection()
        return conn.codeRegister(code)

    def codeRequestSMS(self):
        conn = self.__liteConnection()
        return conn.codeRequestSMS()

    def codeRequestVoice(self):
        conn = self.__liteConnection()
        return conn.codeRequestVoice()