from sampy import *

cli1 = SAMPIntegratedClient(metadata = {
        "samp.name": "VOSpace", 
        "samp.description.text": "Send and receive files to/from VOSpace", 
        "cli1.version": "0.1"})


cli1.connect()

print "CLI1", cli1.getPrivateKey(), cli1.getPublicId()

# Function called when a notification is received

def test_receive_notification(private_key, sender_id, mtype, params, extra):
    print "Notification:", private_key, sender_id, mtype, params, extra
    
# Function called when a call is received
def test_receive_call(private_key, sender_id, msg_id, mtype, params, extra):
    print "Call:", private_key, sender_id, msg_id, mtype, params, extra
    cli1.ereply(msg_id, SAMP_STATUS_OK, result = {"txt": "printed"})

# Function called when a response is received
def test_receive_response(private_key, sender_id, msg_id, response):
    print "Response:", private_key, sender_id, msg_id, response

cli1.bindReceiveNotification("samp.app.*", test_receive_notification)
cli1.bindReceiveCall("samp.app.*", test_receive_call)
