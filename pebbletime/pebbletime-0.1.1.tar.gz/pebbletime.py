#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 Adrian Perez <aperez@igalia.com>
#
# Distributed under terms of the MIT license.

import aiohttp
import gnarl


class BasaltColor(object):
    pass


BASE_URL = "https://timeline-api.getpebble.com/v1"


SchemaString = gnarl.And(str, len)



class PinLayoutType(gnarl.Enum):
    GENERIC      = "genericPin"
    CALENDAR     = "calendarPin"
    REMINDER     = "genericReminder"
    NOTIFICATION = "genericNotification"
    COMM         = "commNotification"
    WEATHER      = "weatherPin"
    SPORTS       = "sportsPin"


class PinIcon(gnarl.Enum):
    GENERIC     = "system://images/NOTIFICATION_GENERIC"
    REMINDER    = "system://images/NOTIFICATION_REMINDER"
    FLAG        = "system://images/NOTIFICATION_FLAG"
    FBMESSENGER = "system://images/NOTIFICATION_FACEBOOK_MESSENGER"
    WHATSAPP    = "system://images/NOTIFICATION_WHATSAPP"
    GMAIL       = "system://images/NOTIFICATION_GMAIL"
    FACEBOOK    = "system://images/NOTIFICATION_FACEBOOK"
    HANGOUTS    = "system://images/NOTIFICATION_GOOGLE_HANGOUTS"
    TELEGRAM    = "system://images/NOTIFICATION_TELEGRAM"
    TWITTER     = "system://images/NOTIFICATION_TWITTER"
    GINBOX      = "system://images/NOTIFICATION_GOOGLE_INBOX"
    MAILBOX     = "system://images/NOTIFICATION_MAILBOX"
    OUTLOOK     = "system://images/NOTIFICATION_OUTLOOK"
    INSTAGRAM   = "system://images/NOTIFICATION_INSTAGRAM"
    BBM         = "system://images/NOTIFICATION_BLACKBERRY_MESSENGER"
    LINE        = "system://images/NOTIFICATION_LINE"
    SNAPCHAT    = "system://images/NOTIFICATION_SNAPCHAT"
    WECHAT      = "system://images/NOTIFICATION_WECHAT"
    VIBER       = "system://images/NOTIFICATION_VIBER"
    SKYPE       = "system://images/NOTIFICATION_SKYPE"
    YAHOOMAIL   = "system://images/NOTIFICATION_YAHOO_MAIL"

    # Generic icons.
    GENERIC_EMAIL    = "system://images/GENERIC_EMAIL"
    GENERIC_SMS      = "system://images/GENERIC_SMS"
    GENERIC_WARNING  = "system://images/GENERIC_WARNING"
    GENERIC_CONFIRM  = "system://images/GENERIC_CONFIRMATION"
    GENERIC_QUESTION = "system://images/GENERIC_QUESTION"

    # Weather icons.
    PARTLY_CLOUDY       = "system://images/PARTLY_CLOUDY"
    CLOUDY_DAY          = "system://images/CLOUDY_DAY"
    LIGHT_SNOW          = "system://images/LIGHT_SNOW"
    LIGHT_RAIN          = "system://images/LIGHT_RAIN"
    HEAVY_RAIN          = "system://images/HEAVY_RAIN"
    HEAVY_SNOW          = "system://images/HEAVY_SNOW"
    TIMELINE_WEATHER    = "system://images/TIMELINE_WEATHER"
    TIMELINE_SUN        = "system://images/TIMELINE_SUN"
    RAINING_AND_SNOWING = "system://images/RAINING_AND_SNOWING"
    TIDE_IS_HIGH        = "system://images/TIDE_IS_HIGH"

    # Timeline item icons.
    TIMELINE_MISSED_CALL = "system://images/TIMELINE_MISSED_CALL"
    TIMELINE_CALENDAR    = "system://images/TIMELINE_CALENDAR"
    TIMELINE_SPORTS      = "system://images/TIMELINE_SPORTS"
    TIMELINE_BASEBALL    = "system://images/TIMELINE_BASEBALL"

    # Sports.
    AMERICAN_FOOTBALL = "system://images/AMERICAN_FOOTBALL"
    CRICKET_GAME      = "system://images/CRICKET_GAME"
    SOCCER_GAME       = "system://images/SOCCER_GAME"
    HOCKEY_GAME       = "system://images/HOCKEY_GAME"

    RESULT_DISMISSED = "system://images/RESULT_DISMISSED"
    RESULT_DELETED   = "system://images/RESULT_DELETED"
    RESULT_MUTE      = "system://images/RESULT_MUTE"
    RESULT_SENT      = "system://images/RESULT_SENT"
    RESULT_FAILED    = "system://images/RESULT_FAILED"

    STOCKS_EVENT    = "system://images/STOCKS_EVENT"
    MUSIC_EVENT     = "system://images/MUSIC_EVENT"
    BIRTHDAY_EVENT  = "system://images/BIRTHDAY_EVENT"
    SCHEDULED_EVENT = "system://images/SCHEDULED_EVENT"
    MOVIE_EVENT     = "system://images/MOVIE_EVENT"

    PAY_BILL                  = "system://images/PAY_BILL"
    HOTEL_RESERVATION         = "system://images/HOTEL_RESERVATION"
    NEWS_EVENT                = "system://images/NEWS_EVENT"
    DURING_PHONE_CALL         = "system://images/DURING_PHONE_CALL"
    CHECK_INTERNET_CONNECTION = "system://images/CHECK_INTERNET_CONNECTION"
    GLUCOSE_MONITOR           = "system://images/GLUCOSE_MONITOR"
    ALARM_CLOCK               = "system://images/ALARM_CLOCK"
    CAR_RENTAL                = "system://images/CAR_RENTAL"
    DINNER_RESERVATION        = "system://images/DINNER_RESERVATION"
    RADIO_SHOW                = "system://images/RADIO_SHOW"
    AUDIO_CASSETTE            = "system://images/AUDIO_CASSETTE"
    SCHEDULED_FLIGHT          = "system://images/SCHEDULED_FLIGHT"
    NO_EVENTS                 = "system://images/NO_EVENTS"
    REACHED_FITNESS_GOAL      = "system://images/REACHED_FITNESS_GOAL"
    DAY_SEPARATOR             = "system://images/DAY_SEPARATOR"
    WATCH_DISCONNECTED        = "system://images/WATCH_DISCONNECTED"
    TV_SHOW                   = "system://images/TV_SHOW"


class Layout(gnarl.Schemed):
    Type = PinLayoutType
    Icon = PinIcon

    __schema__ = {
        "type"  : Type,
        "title" : SchemaString,

        # The rest are all kind-of optional, and their required presence
        # depends on the type (which is the only mandatory field)
        "shortTitle"      : gnarl.Optional(SchemaString),
        "subtitle"        : gnarl.Optional(SchemaString),
        "body"            : gnarl.Optional(SchemaString),
        "tinyIcon"        : gnarl.Optional(Icon),
        "largeIcon"       : gnarl.Optional(Icon),
        "primaryColor"    : gnarl.Optional(gnarl.Use(BasaltColor)),
        "secondaryColor"  : gnarl.Optional(gnarl.Use(BasaltColor)),
        "backgroundColor" : gnarl.Optional(gnarl.Use(BasaltColor)),
        "headings"        : gnarl.Optional([SchemaString]),
        "paragraphs"      : gnarl.Optional([SchemaString]),
        "lastUpdated"     : gnarl.Optional(gnarl.Timestamp),
        "locationName"    : gnarl.Optional(SchemaString),
        "sender"          : gnarl.Optional(SchemaString),
        "broadcaster"     : gnarl.Optional(SchemaString),
        "rankAway"        : gnarl.Optional(SchemaString),
        "rankHome"        : gnarl.Optional(SchemaString),
        "nameAway"        : gnarl.Optional(SchemaString),
        "nameHome"        : gnarl.Optional(SchemaString),
        "recordAway"      : gnarl.Optional(SchemaString),
        "recordHome"      : gnarl.Optional(SchemaString),
        "scoreAway"       : gnarl.Optional(SchemaString),
        "scoreHome"       : gnarl.Optional(SchemaString),
        "sportsGameState" : gnarl.Optional(SchemaString),
    }

    TYPE_REQUIRED_FIELDS = {
        Type.GENERIC      : ("tinyIcon",),
        Type.CALENDAR     : (),
        Type.REMINDER     : ("tinyIcon",),
        Type.NOTIFICATION : ("tinyIcon",),
        Type.COMM         : ("tinyIcon", "sender",),
        Type.WEATHER      : ("tinyIcon", "largeIcon", "locationName",),
        Type.SPORTS       : ("tinyIcon", "largeIcon",)
    }

    def __check_fields(self):
        for field in self.TYPE_REQUIRED_FIELDS.get(self.type, ()):
            if not hasattr(self, field):
                raise ValueError("'{}' is required by layout {}".format(
                    field, self.type.name))

    def __init__(self, title, type=Type.GENERIC, *arg, **kw):
        super(Layout, self).__init__(title=title, type=type, *arg, **kw)

        # Check required fields depending on the layout type.
        self.__check_fields()

        # Check that both headings and paragraphs are provided together.
        if hasattr(self, "paragraphs") or hasattr(self, "headings"):
            if not hasattr(self, "paragraphs"):
                raise ValueError("Expected paragraphs")
            if not hasattr(self, "headings"):
                raise ValueError("Expected headings")
            if len(self.headings) != len(self.paragraphs):
                raise ValueError("Number of headings must be the "
                        "same as number of paragraphs")


class Action(gnarl.Schemed):
    __schema__ = {
        "type"       : SchemaString,
        "launchCode" : gnarl.Optional(int),
        "title"      : gnarl.Optional(SchemaString),
    }

    def __init__(self, type, title=None, launchCode=None):
        params = { "type" : type }
        if title is not None:
            params["title"] = str(title)
        if launchCode is not None:
            params["launchCode"] = int(launchCode)
        super(Action, self).__init__(**params)


class Reminder(gnarl.Schemed):
    __schema__ = {
        "time"   : gnarl.Timestamp,
        "layout" : gnarl.Optional(Layout),
    }

    def __init__(self, time, layout=None):
        params = { "time" : time }
        if layout is not None:
            params["layout"] = layout
        super(Reminder, self).__init__(**params)


class Notification(gnarl.Schemed):
    __schema__ = {
        "layout" : Layout,
        "time"   : gnarl.Optional(gnarl.Timestamp),
    }

    def __init__(self, time, layout):
        super(Notification, self).__init__(time=time, layout=layout)


class Pin(gnarl.Schemed):
    Icon = PinIcon

    __schema__ = {
        "id"     : SchemaString,
        "time"   : gnarl.Timestamp,
        "layout" : Layout,

        "icon"               : gnarl.Optional(Icon),
        "actions"            : gnarl.Optional([Action]),
        "duration"           : gnarl.Optional(int),
        "reminders"          : gnarl.Optional([Reminder]),
        "createNotification" : gnarl.Optional(Notification),
        "updateNotification" : gnarl.Optional(Notification),
    }

    def __init__(self, id, time, layout, **kw):
        super(Pin, self).__init__(id=id, time=time, layout=layout, **kw)


class Timeline(object):
    error_code = {
        400: 'The pin object submitted was invalid.',
        403: 'The API key submitted was invalid.',
        410: 'The user token submitted was invalid or does not exist.',
        429: 'Server is sending updates too quickly.',
        503: 'Could not save pin due to a temporary server error.',
    }

    def __init__(self, api_key, base_url=BASE_URL):
        self.base_url = str(base_url)
        self._session = aiohttp.ClientSession(headers = {
                "Content-Type" : "application/json",
                "X-API-Key"    : str(api_key),
            })

    def __del__(self):
        self._session.close()

    def __check_response(self, response, json=False):
        if json:
            data = yield from response.json()
        else:
            data = yield from response.text()
        return response.status, data

    def send_shared_pind(self, topics, pin):
        response = yield from self._session.put(
                "{.base_url!s}/shared/pins/{.id!s}".format(self, pin),
                headers = { "X-PIN-Topics": ",".join(str(t) for t in topics) },
                data = pin.to_json())
        _ = yield from self.__check_response(response)

    def send_user_pin(self, user_token, pin):
        response = yield from self._session.put(
                "{.base_url!s}/user/pins/{.id!s}".format(self, pin),
                headers = { "X-User-Token": str(user_token) },
                data = pin.to_json())
        _ = yield from self.__check_response(response)

    def delete_user_pin(self, user_token, pin=None, pin_id=None):
        if pin_id is None:
            pin_id = pin.id
        response = yield from self._session.delete(
                "{.base_url!s}/user/pins/{!s}".format(self, pin_id),
                headers = { "X-User-Token": str(user_token) })
        _ = yield from self.__check_response(response)

    def subscribe(self, user_token, topic):
        response = yield from self._session.post(
                "{.base_url!s}/subscription/{!s}".format(self, topic),
                headers = { "X-User-Token": str(user_token) })
        _ = yield from self.__check_response(response)

    def unsubscribe(self, user_token, topic):
        response = yield from self._session.delete(
                "{.base_url!s}/subscription/{!s}".format(self, topic),
                headers = { "X-User-Token": str(user_token) })
        _ = yield from self.__check_response(response)
