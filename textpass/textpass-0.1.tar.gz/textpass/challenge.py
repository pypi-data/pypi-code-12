import logging
import os
from string import digits
from random import choice
from . import db, app
from .models import User
from twilio import TwilioRestException
from twilio.rest import TwilioRestClient


def _get_twilio_client():
    try:
        ACCOUNT_SID = os.environ['TWILIO_SID']
        AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']
    except KeyError as e:
        message = 'Twilio credentials not defined: %s' % (e,)
        logging.error(message)
        print message
        raise IndexError
    return TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)


def _generate_challenge():
    return ''.join(choice(digits) for _ in xrange(6))


def is_correct_answer(phone, answer):
    u = User.query.filter_by(phone=phone).first()
    if not u:
        raise IndexError
        logging.error('No user found for phone: %s', phone)
        return None
    elif u.challenge == answer:
        return u
    else:
        raise KeyError
        logging.error('Answer invalid: %s', answer)
        return None


def request_challenge(phone):
    challenge = _generate_challenge()
    client = _get_twilio_client()
    u = store_challenge(phone, challenge)
    TWILIO_FROM = app.config['TWILIO_FROM']
    if not TWILIO_FROM:
        raise KeyError
    try:
        client.messages.create(
            to=phone,
            from_=TWILIO_FROM,
            body=challenge
        )
    except TwilioRestException as e:
        raise ValueError
        logging.error('Twilio error: %s', e)
    return u


def verify_answer(phone, answer):
    token = None
    u = is_correct_answer(phone, answer)
    if u:
        token = u.generate_auth_token()
    return token


def store_challenge(phone, challenge):
    return User(phone, challenge).get_or_create()
