from .messenger import Messenger
import falcon, json

class FalconMessenger(Messenger):
   def __init__(self, *args, **kwargs):
      super(FalconMessenger, self).__init__(*args, **kwargs)
   
   def on_get(self, req, resp):
      if req.params['hub.verify_token'] == self.verify:
          resp.body = req.params['hub.challenge']
      else:
          resp.body = 'Error'

   def on_post(self, req, resp):
      if req.content_length in (None, 0):
         return
      body = req.stream.read()
      if not body:
         raise falcon.HTTPBadRequest('Empty request body')
      try:
         j = json.loads(body.decode('utf-8'))
      except (ValueError, UnicodeDecodeError):
         raise falcon.HTTPError(falcon.HTTP_753, 'Malformed JSON')
      self.handle_request(j)
