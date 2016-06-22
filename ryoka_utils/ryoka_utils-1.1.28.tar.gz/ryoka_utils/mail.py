#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import smtplib
from email.MIMEText import MIMEText
from email.Header import Header
from email.Utils import formatdate

reload(sys)
sys.setdefaultencoding("utf-8")

class SendGmail:
  def __init__(self, encoding, subject, body, from_addr, to_addr, login_addr, passwd):
    self.date = formatdate()
    self.encoding = encoding
    self.subject = subject
    self.body = body.encode(encoding)
    self.from_addr = from_addr
    self.to_addr = to_addr
    self.login_addr = login_addr
    self.passwd = passwd

  def sendMail(self):
    msg = MIMEText(self.body, 'plain', self.encoding)
    msg['Subject'] = Header(self.subject, self.encoding)
    msg['From'] = self.from_addr
    msg['To'] = self.to_addr
    msg['Date'] = self.date

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(self.login_addr, self.passwd)
    s.sendmail(self.from_addr, self.to_addr, msg.as_string())
    s.close()

class SendMail:
    def __init__(self):
        self.from_address = None
        self.to_address = None
        self.password = None
        self.title = None
        self.body = None
        self.charcode = "utf-8"

    def set_from_address(self, address):
        self.from_address = address

    def set_to_address(self, address):
        self.to_address = address

    def set_password(self, password):
        self.password = password

    def set_title(self, title):
        self.title = title

    def set_body(self, body):
        self.body = body

    def set_charcode(self, code):
        self.charcode = code

    def send(self):
        gmail = SendGmail(self.charcode, self.title, self.body, self.from_address, self.to_address, self.from_address, self.password)
        gmail.sendMail()
