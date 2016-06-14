import emails

imgfn = 'roasted-asparagus.jpg'

msg_To = "sah@blackearthgroup.com"
msg_From = "sah@blackearth.us"
msg_subject = "Email Test"
msg_text = "Take a look at the attached picture of asparagus.\n\n-Sean"
msg_html = '<b>Take a look at this picture of asparagus:</b><br><img src="cid:%s"><br>' % imgfn

msg = emails.Message(html=msg_html, text=msg_text, subject=msg_subject, mail_from=msg_From)
msg.attach(filename=imgfn, content_disposition="inline", data=open(imgfn, 'rb'))
response = msg.send(to=msg_To, smtp={'host':'localhost', 'port':25})

print(response)
