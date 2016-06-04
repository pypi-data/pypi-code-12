#loop.add_signal_handler(signal.SIGINT, stop)
"""Sample Slack ping bot using asyncio and websockets."""
import asyncio
import json
import signal
import sys
import aiohttp
import websockets

from api import call


DEBUG = True
TOKEN = "xoxb-38220681028-F9HLfx7SpQrn8zj8RHrQD5vb"
RUNNING = True

async def api_call(method, **kwargs):
    return await call(method, token=TOKEN, **kwargs)

async def getChannel(user_id):
    chan = await api_call("im.open", user=user_id)
    print(chan)
    return chan['channel']['id']

async def sendMessage(chan, txt):
    await api_call("chat.postMessage", as_user="true", channel=chan, text=txt)

#{ eleve1 : { "C++ avec Qt" : "X", "Projet P2 conception" : "p" },
#  eleve2 : ...
async def sendRappel(eleve, classe, cours):
    print(eleve)
    channel_id = await getChannel(eleve)
    await sendMessage(channel_id, formatMessage(classe, cours))

#sendRappel("2016.7.3")


async def sendDate(user_id, date):
    for classe in plan[date]:
        for eleve in sub[classe]:
            print(eleve + classe)
            await sendRappel(eleve, classe, plan[date][classe])
        for cours in plan[date][classe]:
            for eleve in sub[cours]:
                print(eleve + classe + cours)
                test = {cours : plan[date][classe][cours]}
                await sendRappel(eleve, classe, test)

#async def sendDate(user_id, date):
#    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"+user_id)
#    for classe in plan[date]:
#        if user_id in sub[classe]:
#            await sendRappel(user_id, classe, plan[date][classe])
#        else:
#            for eleve in sub[classe]:
#    			#print(eleve + classe)
#                await sendRappel(eleve, classe, plan[date][classe])
#        for cours in plan[date][classe]:
#            if user_id in sub[cours]:
#                await sendRappel(user_id, classe, plan[date][classe])
#            else:
#                for eleve in sub[cours]:
#    				#print(eleve + classe + cours)
#                    test = {cours : plan[date][classe][cours]}
#                    await sendRappel(eleve, classe, test)

def formatMessage(classe, cours):
	d = {"X" : "une evalution !", "p" : "le projet à continuer"}
	message = "Bonjour, avec la classe "+classe+","
	print(cours)
	for nom in cours:
		message += "en "+nom+", vous avez "+d[cours[nom]]+"\n"
	return message

async def showHelp(user_id, message):
    message = " Liste des commande :\n" \
            + " help : affiche l'aide\n" \
            + " print date : envoie à tous les inscrits la liste des projet/eval qui les concernent\n" \
            + " subme cours ou classe : inscrit la personne qui à envoyer le message au cours ou à la classe passé\n\n" \
            + " Liste des cours :\n"
    for key in sub:
        message += key + "\n"
    channel_id = await getChannel(user_id)
    await sendMessage(channel_id, message)

async def getWarning(user_id, message):
    await sendDate(user_id, message)

async def subscribe(user_id, message):
    sub[message].add(user_id)
    print(sub)

async def error(user_id, message):
    pass

#http://stackoverflow.com/questions/5125619/why-list-doesnt-have-safe-get-method-like-dictionary
def safe_list_get (l, idx, default):
  try:
    return l[idx]
  except IndexError:
    return default

async def consumer(message):
    """Display the message."""
    if message.get('type') == 'message':
        user = await api_call('users.info', user=message.get('user'))
        parameter = message["text"].split(" ", 1)
        #print("{0}: {1}".format(user["user"]["name"],
        #                        message["text"]))
        action = d.get(parameter[0]) or error
        option = safe_list_get(parameter, 1, "2016.7.3")
        await action(message.get('user'),option)
    else:
        print(message, file=sys.stderr)

async def bot(token=TOKEN):
    print(await api_call("api.test"))

    """Create a bot that joins Slack."""
    rtm = await api_call("rtm.start")
    assert rtm['ok'], "Error connecting to RTM."

    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(rtm["url"]) as ws:
            async for msg in ws:
                assert msg.tp == aiohttp.MsgType.text
                message = json.loads(msg.data)
                asyncio.ensure_future(consumer(message))

def stop():
    global RUNNING
    RUNNING = false
    print("STOP")

d = { "help" : showHelp,  "print" : getWarning, "subme" : subscribe}

plan = { "2016.7.3" : { "INF2dlm-a" : { "C++ avec Qt" : "X" , "Projet P2 conception" : "p"},
						"INF2dlm-b" : { "C++ avec Qt" : "X" , "Projet P2 conception" : "p"},
					  },
		 "2016.7.4" : { "INF2dlm-a" : { "Projet P2 conception" : "p"},
						"INF2dlm-b" : { "Application web" : "p" , "Réseaux et applications" : "p" ,"Projet P2 conception" : "p"},
					  },
		 "2016.7.5" : { "INF2dlm-a" : { "Application web" : "p" , "Projet P2 conception" : "p"},
						"INF2dlm-b" : { "Projet P2 conception" : "p"},
					  }
	   }

sub = { "INF2dlm-a" : set(),
		"INF2dlm-b" : set(),
		"C++ avec Qt" : set(),
		"Projet P2 conception" : set(),
		"Application web" : set(),
		"Réseaux et applications" : set()
	  }

if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    loop.set_debug(DEBUG)
    #loop.add_signal_handler(signal.SIGINT, stop)
    loop.run_until_complete(bot(TOKEN))
    loop.close()
