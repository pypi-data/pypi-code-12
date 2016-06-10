# -*- coding: utf-8 -*-
# Copyright James Gardner MIT license


import requests
from behave import *


@step('1 email has been sent')
def step_impl(context):
    context.execute_steps('Then 1 emails have been sent')


@step('{count:d} emails have been sent')
def step_impl(context, count):
    lathermail_host = context.config.userdata['lathermail_host']
    r = requests.get(lathermail_host+'/api/0/messages/', headers = {'X-Mail-Password': 'password'})
    assert r.status_code == 200, 'Non-200 response: {}\n{}'.format(r.status_code, r.text)
    json_data = r.json()
    assert count == json_data['message_count'], 'count: {}, JSON: {}'.format(count, json_data)


@step('I clear any sent emails')
def step_impl(context):
    lathermail_host = context.config.userdata['lathermail_host']
    r = requests.delete(lathermail_host+'/api/0/messages/', headers = {'X-Mail-Password': 'password'})
    assert r.status_code == 204, 'Non-204 response: {}\n{}'.format(r.status_code, r.text)


@step('I fetch the first sent email')
def step_impl(context):
    context.execute_steps('Then I fetch sent email number 1')


@step('I fetch sent email number {number:d}')
def step_impl(context, number):
    lathermail_host = context.config.userdata['lathermail_host']
    r = requests.get(lathermail_host+'/api/0/messages/', headers = {'X-Mail-Password': 'password'})
    assert r.status_code == 200, 'Non-200 response: {}\n{}'.format(r.status_code, r.text)
    json_data = r.json()
    assert number > 0
    assert json_data['message_count'] >= (number-1), 'No such message {}, JSON: {}'.format(number, json_data)
    context.message = json_data['message_list'][(number-1)]


#
# Message assertions
#


@step('the email is to "{recipient}"')
def step_impl(context, recipient):
    assert context.message['recipients_raw'] == recipient


@step('the email is from "{sender}"')
def step_impl(context, sender):
    assert context.message['sender_raw'] == sender


@step('the email subject is "{subject}"')
def step_impl(context, subject):
    assert context.message['subject'] == subject


@step('the email body contains "{text}"')
def step_impl(context, text):
    assert text in context.message['message_raw']
