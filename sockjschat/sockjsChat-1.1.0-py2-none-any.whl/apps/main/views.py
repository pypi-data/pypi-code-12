import tornado.web
import tornado.escape

from sockjs.tornado import SockJSConnection

print '\n\ninvoked apps.main.views.py\n'

class IndexHandler(tornado.web.RequestHandler):
    """Regular HTTP handler to serve the chatroom page"""
    print "\n\ninvoked IndexHandler\n"
    def get(self):
    	print "\ninside IndexHandler get()"
        self.render('index.html')
        



# Connections
print "current Participant :"
participants=set()
print participants
print

class groupConnection(SockJSConnection):
	print '\n\nInvoked groupConnection\n'
	def on_open(self, info):
		print '\ninside groupConnection on_open()'
		print  "current participants : ",participants
		participants.add(self)
		print "updated participants : ",participants
		print 'returning from groupConnection on_open'

	def on_message(self, message):
		print '\ninside groupConnection on_message()'
		print 'self participant : ',self
		print  "current participants : ",participants
		print "message sent : ",message
		res = tornado.escape.json_decode(message)
		print "json_decode message : ",res
		if res['stage']=='start':
			print 'inside res[stage]==start'
			print "broadcasting... ***** name joined ****"
			self.broadcast(participants, '***** '+res['name']+' joined *****')
		elif res['stage']=='end':
			# print  "current participants : ",participants
			print 'inside res[stage]==end'
			print "broadcasting... ***** name joined ****"
			self.broadcast(participants, '***** '+res['name']+' left *****')
			print 'invoking participant.revove(self)'
			participants.remove(self)
			print 'updated participants : ',participants

		else:
			print 'inside res[stage]==process'
			print 'broadcating... [name] message'
			self.broadcast(participants, '['+res['name']+']  ' + res['message'])
		print 'returning from groupConnection on_message'

	def on_close(self,name):
		print '\ninside groupConnection on_message()'
		print  "current participants : ",participants
		participants.remove(self)
		print "message sent : ",message
		print 'broadcastting.... ***** name left ****'
		self.broadcast(participants,'*** '+name+' left ***')
		print 'returning from groupConnection on_close'


	    
	    

	

class privateConnection(SockJSConnection):
    def on_open(self, info):
        self.send('Carl says goodbye!')
        participants.add(self)

    def on_message(self,message):
	    pass

	
    def on_close(self):
	    participants.remove(self)
	    self.broadcast(participants,'Carl Left')


