def sendmail(fromAddress, toAddress, mPassword, mServer, mPort, mSubject, mMessage="", mMessageHTML="", mAttachment=None, displaySend=True):
  import smtplib
  from email.mime.multipart import MIMEMultipart
  from email.mime.image import MIMEImage
  from email.mime.base import MIMEBase
  from email.mime.audio import MIMEAudio
  from email import encoders
  from email.mime.text import MIMEText
  import mimetypes
  import os

  msg = MIMEMultipart('alternative')
  msg['From'] = fromAddress
  msg['To'] = toAddress
  msg['Subject'] = mSubject
  body = mMessage
  bodyHTML = mMessageHTML
  partText = MIMEText(mMessage, 'plain')
  partHTML = MIMEText(mMessageHTML, 'html')
  msg.attach(partText)
  msg.attach(partHTML)

  if mAttachment:
    for i in mAttachment:
      fp = open(i, 'rb')
      ctype, encoding = mimetypes.guess_type(i)
      if ctype is None or encoding is not None:
        ctype = 'application/octet-stream'
      maintype, subtype = ctype.split('/', 1)
      if maintype == 'text':
        attachment = MIMEText(fp.read(), _subtype=subtype)
      elif maintype == 'image':
        attachment = MIMEImage(fp.read(), _subtype=subtype)
      elif maintype == 'audio':
        attachment = MIMEAudio(fp.read(), _subtype=subtype)
      else:
        attachment = MIMEBase(maintype, subtype)
        attachment.set_payload(fp.read())
        encoders.encode_base64(msg)
      fp.close()
      msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(i))
      msg.attach(i)

  if displaySend==False:
    s = smtplib.SMTP(mServer,mPort)
    text = msg.as_string()
    send=s.sendmail(fromAddress, toAddress, text)
    s.quit()
  else:
    s = smtplib.SMTP(mServer, mPort)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(fromAddress, mPassword)
    text = msg.as_string()
    send=s.sendmail(fromAddress, toAddress, text)
    s.quit()
  if send=={}:
    print ("Sending successful")