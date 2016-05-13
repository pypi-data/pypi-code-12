# -*- coding: utf-8 -*-
import codecs
from markdown import markdown

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

from ConfigParser import NoSectionError
from ConfigParser import SafeConfigParser
parser = SafeConfigParser()
parser.read('mail_config.ini')


def generate_config():
    """生成邮件配置文件
    """
    config = """[mail_config]
sender = your email
password = your password
receivers = lining@luojilab.com
    """
    with open("mail_config.ini", "w") as f:
        f.write(config)


def luoji_mail(subject, body_file):
    """邮件发送服务
    params:
        subject:      邮件标题
        body_file:    Markdown格式的邮件正文 文件
    """
    # 获取配置文件mail_config中的参数
    try:
        sender = parser.get('mail_config', 'sender')
        password = parser.get('mail_config', 'password')
        receivers = parser.get('mail_config', 'receivers').split(',')
    except NoSectionError:
        print """
        Use 'ljmail-generate-config' to generate 'mail_config' file
        """
        return

    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = ';'.join(receivers)
    msg['Subject'] = subject

    # 读取markdown 邮件主体文件，支持中文，先转码为utf-8
    try:
        with codecs.open(body_file, encoding='utf-8', mode='r') as f:
            content = markdown(f.read())
    except Exception:
        print """
        Create a Markdown file in the present working directory called body.md
        """
        return

    msg.attach(MIMEText(content.encode('utf-8'), 'html'))
    text = msg.as_string()

    try:
        server = smtplib.SMTP_SSL(host='smtp.exmail.qq.com',
                                  port=465)
        server.login(sender, password)
        server.sendmail(sender, receivers, text)
        print 'Successfully sent mail'
    except Exception as e:
        print 'Error happens: %s' % e.message
        print "Check the mail_config.ini to ensure that it can send email"
    finally:
        server.quit()
