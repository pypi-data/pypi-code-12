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
        for messaging in entry['messaging']:
            if not 'message' in messaging:
                continue
            message = messaging['message']
            self.handle_message(messaging['sender']['id'],
               message.get('text', None), message.get('attachments', None))

    def handle_message(self, recipient_id, text, attachments):
        self.reply(recipient_id,
           self.transform_message(text, attachments))

    def reply(self, recipient_id, message):
        requests.post(self.fb_url,
            params={'access_token': self.token},
            json={
                'recipient': {'id': recipient_id},
                'message': {'text': message}
                }
            )

    def transform_message(self, text, attachments):
        if text:
            return text
        if attachments:
            return 'attachments'
        return 'Nothing'
