import requests

class Messenger:
   def __init__(self, verify, token,
		fb_url='https://graph.facebook.com/v2.6/me/messages'):
      self.verify = verify
      self.token = token
      self.fb_url = fb_url
   
   def handle_request(self, j):
      for entry in j['entry']:
         self.handle_entry(entry)
   
   def handle_entry(self, entry):
      for message in entry['messaging']:
         if not 'message' in message or 'text' not in message['message']:
             continue
         self.handle_message(message)

   def handle_message(self, message):
      self.reply(message['sender']['id'],
		 self.transform_message(message['message']['text']))

   def reply(self, sender, message):
      requests.post(self.fb_url,
        params={'access_token': self.token},
        json={
            'recipient': {'id': sender},
            'message': {'text': message}
	}
      )

   def transform_message(self, message):
      return message
