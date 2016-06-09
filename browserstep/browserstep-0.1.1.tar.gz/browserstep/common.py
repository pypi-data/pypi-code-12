# -*- coding: utf-8 -*-
# Copyright James Gardner MIT license

import os
import time

from behave import *


@step('I navigate to /{path}')
def step_impl(context, path):
    context.browser.get(context.config.userdata['test_host'] + '/' + path)

@step('I navigate to /')
def step_impl(context):
    context.browser.get(context.config.userdata['test_host'] + '/')

@step('the browser moves to /{path}')
def step_impl(context, path):
    expected_url = context.config.userdata['test_host'] + '/' + path
    assert expected_url == context.browser.current_url, "Expected browser to be at {!r} but it as at {!r}".format(expected_url, context.browser.current_url)

@step('the browser moves to /')
def step_impl(context):
    expected_url = context.config.userdata['test_host'] + '/'
    assert expected_url == context.browser.current_url, "Expected browser to be at {!r} but it as at {!r}".format(expected_url, context.browser.current_url)

@step('the browser is still at /{path}')
def step_impl(context, path):
    context.execute_steps('Then the browser moves to /{}'.format(path))

@step('the browser is still at /')
def step_impl(context, path):
    context.execute_steps('Then the browser moves to /')

@step('I click on "{selector}"')
def step_impl(context, selector):
    element = context.browser.find_element_by_css_selector(selector)
    assert element is not None, "No such element found"
    element.click()

@step('I follow the "{text}" link')
def step_impl(context, text):
    element = context.browser.find_element_by_link_text(text)
    assert element is not None, "No such link found"
    element.click()

@step('I click the "{text}" button')
def step_impl(context, text):
    element = context.browser.find_element_by_xpath("//button[contains(text(), '{}')] | //input[contains(text(), '{}')] ".format(text, text))
    assert element is not None, "No such button found"
    element.click()

@step('I wait for {seconds:f} second(s)')
def step_impl(context, seconds):
    time.sleep(seconds)

@step('I wait for {seconds:d} second(s)')
def step_impl(context, seconds):
    time.sleep(seconds)

@step('there are {n} "{selector}" elements in "{container_selector}"')
def step_impl(context, n, selector, container_selector):
    container = context.browser.find_element_by_css_selector(container_selector)
    elements = container.find_elements_by_css_selector(selector)
    assert len(elements) != n, "Expected {} elements, got {}".format(n, len(elements))

@step('there is 1 "{selector}" element in "{container_selector}"')
def step_impl(context, selector, container_selector):
    context.execute_steps('Then there are 1 "%s" elements in "%s"' % (selector, container_selector))

@step('there are {n:d} "{selector}" elements')
def step_impl(context, n, selector):
    context.execute_steps('Then there are %d "%s" elements in "html"' % (n, selector))

@step('there is 1 "{selector}" element')
def step_impl(context, selector):
    context.execute_steps('Then there are 1 "%s" elements in "html"' % (selector))

@step('I see "{text}" in "{container}"')
def step_impl(context, text, container):
    element = context.browser.find_element_by_css_selector(container)
    assert element is not None and text in element.get_attribute('textContent'), "Did not find text"

import subprocess

@step('I run the following command')
def step_impl(context):
    context.output = None
    p = subprocess.Popen(
        context.text,
        cwd=context.config.userdata.get("cwd", os.getcwd()),
        shell=True,
        stdout=subprocess.PIPE
    )
    context.output, err = p.communicate()
    assert 0 == p.wait(), "Non-zero exit status"

import difflib

@step('there is no output')
def step_impl(context):
    assert context.output is not None, "No command has been run yet, so there is no output"
    assert context.text == None, 'Unexpected output:\n{!s}'.format(context.text)

@step('the output is')
def step_impl(context):
    assert context.output is not None, "No command has been run yet, so there is no output"
    if context.output != context.text.encode('utf8'):
        s1 = [s+'\n' for s in context.text.split('\n')]
        s2 = [s+'\n' for s in context.output.split('\n')]
        assert False, '\n'+(''.join(difflib.unified_diff(s1, s2, fromfile='expected', tofile='actual')))

@step('I type "{text}" into "{selector}"')
def step_impl(context, text, selector):
    element = context.browser.find_element_by_css_selector(selector)
    assert element is not None, "No such element found"
    element.send_keys(text)

@step('I type the following into "{selector}"')
def step_impl(context, selector):
    element = context.browser.find_element_by_css_selector(selector)
    assert element is not None, "No such element found"
    element.send_keys(context.text)
