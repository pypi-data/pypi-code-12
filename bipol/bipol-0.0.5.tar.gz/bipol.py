from helga.plugins import command, ResponseNotReady
from requests import get
from twisted.internet import reactor

def bipol_async(client, channel, args):
    response = get('http://bipolasaservice.herokuapp.com/bipol')
    client.msg(channel, response.text)

@command('bipol', help='listen to what he has to say')
def bipol(client, channel, nick, message, cmd, args):
    reactor.callLater(0, bipol_async, client, channel, args)
    raise ResponseNotReady

