#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
'''
messages.py

Processes messages utility library

Created by SWS on 2012-09-11.
Copyright (c) 2012 StoneWorkSolutions. All rights reserved.
'''
import json
import logging
import re
import redis
import traceback
import inspect

try:
	from stoneauth.middlewares import StoneThreadLocal as ThreadLocal
except:
	from django_tools.middlewares import ThreadLocal

logger = logging.getLogger('sws-tags')

level_translations = {
	'success': 'info',
	'broadcast': 'info',
}


def getTraceBackInfo():
	info = inspect.stack()[2][3]
	return info


def processErrorsForm(form):

	message = ''
	messages = []

	for field in form:

		if field.errors:
			message = re.sub('</(.*)>', '', unicode(str(field.errors), 'utf-8'))
			message = re.sub('<(.*)>', '', message)
			message = field.html_name + ': ' + message
			messages.append(message)

	return messages


def processMessages(message, typeMessage, timeOut=10000, rsyslog=True):

	msg = {}

	if rsyslog:
		try:
			called_from_view = getTraceBackInfo()
			if type(message) is list:
				for m in message:
					getattr(logger, level_translations.get(typeMessage, typeMessage))(' view: ' + called_from_view + ', user: ' + str(ThreadLocal.get_current_user()) + ', message: ' + m)
			elif type(message) is str:
				getattr(logger, level_translations.get(typeMessage, typeMessage))(' view: ' + called_from_view + ', user: ' + str(ThreadLocal.get_current_user()) + ', message: ' + message)
		except:
			pass

	msg[typeMessage] = (message, timeOut)

	return msg

# Send message to the specific channel
# Parametres:
# 	name channel (session_id or settings.CHANNEL_GLOBAL_MESSAGES)
# 	text message
# 	level (info, warning,error or debug)
# 	time visible


def sendMessages(channel, connection_redis, message='No messages', level='broadcast', time=5000, rsyslog=True):

	message = {"message": message, "level": level, "time": time}
	connection_redis.publish(channel, json.dumps(['user_message', message]))

	if rsyslog:
		try:
			called_from_view = getTraceBackInfo()
			getattr(logger, level_translations.get(level, level))(' channel: ' + channel + ', user: ' + str(ThreadLocal.get_current_user()) + ', message: ' + message['message'])
		except:
			pass

	return True


def sendEvent(channel, connection_redis, event='', data='', rsyslog=True):

	# cr = redis.Redis(**settings.REDIS_SERVERS['std_redis'])

	connection_redis.publish(channel, json.dumps([event, data]))

	if rsyslog:
		try:
			logger.debug('New event\n-Channel: {0}\n-User: {1}\n-Event: {2}\n-Data: {3}'.format(channel, ThreadLocal.get_current_user(), event, data))
		except:
			pass

	return True


def sendProgressBarEvent(channel, connection_redis, view_name='', value='', message='', error=False):
	sendEvent(channel, connection_redis, 'progressbar', {'view_name': view_name, 'value': value, 'message': message, 'error': error})


def sendBubbleNotificationEvent(channel, connection_redis, view_name='', value='', mode='add'):
	sendEvent(channel, connection_redis, 'bubblenotification', {'view_name': view_name, 'value': value, 'mode': mode})


def sendBubbleNotificationBlinkEvent(channel, connection_redis, view_name=''):
	sendEvent(channel, connection_redis, 'bubblenotificationblink', {'view_name': view_name})


def sendDashboardEvent(channel, connection_redis, data=''):
	sendEvent(channel, connection_redis, 'dashboard', {'data': data})


def swslog(typeMessage, message, e, gettraceback=True):

	called_from_view = getTraceBackInfo()

	try:
		if gettraceback:
			getattr(logger, typeMessage)(' -- ' + called_from_view + ', User: ' + str(ThreadLocal.get_current_user()) + ', Message {0}: '.format(typeMessage) + message + ' Exception: {0}'.format(traceback.format_exc()))
		else:
			getattr(logger, typeMessage)(' -- ' + called_from_view + ', User: ' + str(ThreadLocal.get_current_user()) + ', Message {0}: '.format(typeMessage) + message)
	except:
		pass
