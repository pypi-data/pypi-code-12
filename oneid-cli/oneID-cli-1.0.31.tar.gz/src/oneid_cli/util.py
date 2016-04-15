
from __future__ import print_function

import uuid
import argparse

import oneid.service

YES_NO = {
    'yes': True,
    'no': False,
    'y': True,
    'n': False,
    'ye': True
}


def uuid_param(uuid_str):
    """
    argparse `type=` helper for UUIDs

    Note that it returns a `str` rather than a :py:class:`uuid.UUID` type,
    as it is more useful in that form most of the time.

    :param uuid_str: the value of the param passed
    :type uuid_str: str
    :return: the UUID
    :rtype: str
    """
    try:
        return(str(uuid.UUID(uuid_str)))
    except:
        raise argparse.ArgumentTypeError('invalid UUID {}'.format(uuid_str))


def prompt_to_action(action='do that', preamble=None):
    """
    Ask the user if they really want to do something that may be dangerous.

    :param action: text to insert in "Are you sure you want to <action>?"
    :type action: str
    :param preamble: text to display before asking the question
    :type action: str
    :return: the user's answer
    :rtype bool
    """

    if preamble:
        print(preamble)

    while True:
        user_answer = raw_input('Are you sure you want to {}? [yes/N] : '.format(action))
        if user_answer == '':
            user_answer = 'n'
        else:
            user_answer = user_answer.lower()

        if user_answer not in YES_NO:
            print('Sorry, I don\'t understand your answer')
            continue

        answer = YES_NO[user_answer]

        if answer and user_answer != 'yes':
            print('Sorry, I need a full "yes" to continue')
            continue

        return answer


def prompt_to_create_keypair():
    """
    Ask the user if they want a public/private keypair (Keypair) created,
    and if so, do it.

    :param outfile: Filename to save the private key to (optional)
    :type print_key: str
    :return: created Keypair, or None, if not created
    :rtype :py:class:`oneid.keychain.Keypair`
    """
    keypair = None

    while True:
        create_key_choice = raw_input('Would you like me to generate a public/private key pair? [Y/n] : ')
        if create_key_choice == '':
            create_key_choice = 'y'

        if create_key_choice.lower() not in YES_NO:
            print('Sorry, I don\'t understand your answer')
            continue

        if YES_NO[create_key_choice.lower()]:
            keypair = oneid.service.create_secret_key()
        break

    return keypair
