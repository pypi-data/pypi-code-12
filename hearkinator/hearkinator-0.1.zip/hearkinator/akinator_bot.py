"""Sample Slack ping bot using asyncio and websockets."""
import asyncio
import json
import signal
import ast

import aiohttp

import websockets
from slackclient import SlackClient

DEBUG = True
TOKEN = "xoxb-"
RUNNING = True

sc = SlackClient(TOKEN)
print(sc.api_call("api.test"))
userList = sc.api_call("users.list")
listPlayer={}
listAdmin=('julien.baumgart','reziziflag')
botName = "hearkinator"

async def producer():
    """Produce a ping message every 10 seconds."""
    await asyncio.sleep(10)
    return json.dumps({"type": "ping"})


async def consumer(message):
    """Consume the message by printing them."""
    #print(message)
    dico = json.loads(message)
    #for key in dico:
        #if(key == "text"):
        #    print(dico[key])
    if('channel' in dico and 'text' in dico and 'type' in dico and dico['type'] == 'message' and 'user' in dico):
        #sendMessage(dico['channel'], dico['text'])
        command(dico, dico['text'])

async def bot(token):
    """Create a bot that joins Slack."""
    loop = asyncio.get_event_loop()
    with aiohttp.ClientSession(loop=loop) as client:
        async with client.post("https://slack.com/api/rtm.start",
                               data={"token": TOKEN}) as response:
            assert 200 == response.status, "Error connecting to RTM."
            rtm = await response.json()

    async with websockets.connect(rtm["url"]) as ws:
        while RUNNING:
            listener_task = asyncio.ensure_future(ws.recv())
            producer_task = asyncio.ensure_future(producer())

            done, pending = await asyncio.wait(
                [listener_task, producer_task],
                return_when=asyncio.FIRST_COMPLETED
            )

            for task in pending:
                task.cancel()

            if listener_task in done:
                message = listener_task.result()
                await consumer(message)

            if producer_task in done:
                message = producer_task.result()
                await ws.send(message)


def stop():
    """Gracefully stop the bot."""
    global RUNNING
    RUNNING = False
    print("Stopping... closing connections.")

def askOrAnswer(dico):
    if(dico['text'].upper() == "OUI" or dico['text'].upper() == "NON"):
        if(listPlayer[dico['user']]['poseQuestion'] == False and listPlayer[dico['user']]['actif'] == True):
            user2ID = listPlayer[dico['user']]['adversaire']
            sendMessage(dico['channel'], getUserName(user2ID)+" réfléchit :thinking_face:")
            sendMessage(getChannel(user2ID), getUserName(dico['user'])+" a répondu "+dico['text'])
            listPlayer[dico['user']]['actif'] = False
            listPlayer[user2ID]['actif'] = True
    else:
        if (listPlayer[dico['user']]['poseQuestion']):
            user2ID = listPlayer[dico['user']]['adversaire']
            if(listPlayer[dico['user']]['actif']):
                sendMessage(dico['channel'], getUserName(user2ID)+" va répondre à ta question :face_with_rolling_eyes:")
                sendMessage(getChannel(user2ID), getUserName(dico['user'])+" demande: "+dico['text'])
                increaseTurn(dico['user'])
                listPlayer[dico['user']]['actif'] = False
                listPlayer[user2ID]['actif'] = True
            else:
                sendMessage(dico['channel'], "Attends que "+getUserName(user2ID)+" réponde avant de poser une autre question.")



def command(dico, comm):
    """Execute a command for Akinator"""
    list = comm.split( )
    user1Name = getUserName(dico['user'])


    if(list[0] == "start"):
        if(len(list) == 3):
            user2ID = getUserID(list[1])
            if(user2ID != None):
                    if(list[1] == user1Name):
                        sendMessage(dico['channel'], "Tu ne peux pas jouer avec toi-même, même si tu n'as pas d'ami :joy:")
                    elif(list[1] == botName):
                        sendMessage(dico['channel'], "Moi? Ok... Tu penses à "+list[2]+", j'ai gagné. :wink:")
                    else:
                        if(addGame(dico['user'], user2ID, list[2].upper())):
                            sendMessage(dico['channel'], "Tu commences une partie avec "+list[1]+":sunglasses:, tu penses à "+list[2]+".")
                            sendMessage(getChannel(user2ID), "Bonjour "+list[1]+" :sunglasses:, "+user1Name+" veut jouer avec toi, pose-lui des questions pour savoir à quel personnage il pense! ")
                        else:
                            sendMessage(dico['channel'], "Tu ne peux pas jouer avec "+list[1]+" maintenant, l'un de vous deux est déjà en partie avec quelqu'un.")

            else:
                sendMessage(dico['channel'], "Utilisateur inconnu: "+list[1])
        else:
            sendMessage(dico['channel'], "Format: akinator start [joueur] [personnage]")


    elif(list[0] == "personnage"):
        if(len(list) == 1):
            if dico['user'] in listPlayer:
                if(listPlayer[dico['user']]['personnage'] == None):
                    sendMessage(dico['channel'], "Avant de penser à quelqu'un, tu dois trouver le personnage de "+getUserName(listPlayer[dico['user']]['adversaire'])+".")
                else:
                    sendMessage(dico['channel'], "Tu penses à "+listPlayer[dico['user']]['personnage'])
            else:
                sendMessage(dico['channel'], "Tu ne penses à personne, car tu ne joues pas...")
        elif(len(list) == 2):
            if dico['user'] in listPlayer and listPlayer[dico['user']]['poseQuestion'] == False and listPlayer[dico['user']]['actif'] == True and listPlayer[dico['user']]['personnage'] == None:
                user2ID = listPlayer[dico['user']]['adversaire']
                sendMessage(dico['channel'], "Tu penses à "+list[1]+", "+getUserName(user2ID)+" va maintenant te poser des questions.")
                sendMessage(getChannel(user2ID), user1Name+" pense à un personnage, essaie de le trouver.")
                listPlayer[dico['user']]['personnage'] = list[1].upper()
                listPlayer[dico['user']]['actif'] = False
                listPlayer[user2ID]['actif'] = True
            else:
                sendMessage(dico['channel'], "Ce n'est pas le bon moment pour penser à un personnage.")
        else:
            sendMessage(dico['channel'], "Format: (akinator personnage) ou (akinator personnage[nom])")


    elif(list[0] == "stop"):
        if dico['user'] in listPlayer:
            user2ID = listPlayer[dico['user']]['adversaire']
            sendMessage(getChannel(user2ID), user1Name+" a quitté la partie.")
            sendMessage(dico['channel'], "Tu as quitté la partie.")
            del listPlayer[user2ID]
            del listPlayer[dico['user']]
        else:
            sendMessage(dico['channel'], "Tu ne peux pas quitter la partie, car tu ne joues pas...")


    elif(list[0] == "reponse"):
        if(len(list)==2):
            if dico['user'] in listPlayer and listPlayer[dico['user']]['actif']:
                user2ID = listPlayer[dico['user']]['adversaire']
                user2Name = getUserName(user2ID)
                if(listPlayer[user2ID]['personnage'] == list[1].upper()):
                    if(listPlayer[dico['user']]['personnage'] == None):
                        sendMessage(dico['channel'], "Bravo :clap: :clap: :clap: Tu as trouvé le bon personnage en "+str(listPlayer[dico['user']]['nbTours'])+" tours! A toi de choisir un personnage.")
                        sendMessage(getChannel(user2ID), user1Name+" a trouvé le bon personnage en "+str(listPlayer[dico['user']]['nbTours'])+" tours! C'est à son tour de choisir un personnage.")
                        listPlayer[dico['user']]['poseQuestion'] = False
                        listPlayer[user2ID]['poseQuestion'] = True
                    else:
                        if(listPlayer[dico['user']]['nbTours'] > listPlayer[user2ID]['nbTours']):
                            sendMessage(dico['channel'], ":-1: Tu es 2ème! Tu as trouvé le bon personnage en "+str(listPlayer[dico['user']]['nbTours'])+" tours, alors que "+user2Name+" a trouvé en "+str(listPlayer[user2ID]['nbTours'])+" tours")
                            sendMessage(getChannel(user2ID), ":crown: Tu as gagné! Tu as trouvé le bon personnage en "+str(listPlayer[user2ID]['nbTours'])+" tours, alors que "+getUserName(dico['user'])+" a trouvé en "+str(listPlayer[dico['user']]['nbTours'])+" tours")

                        elif(listPlayer[dico['user']]['nbTours'] < listPlayer[user2ID]['nbTours']):
                            sendMessage(getChannel(user2ID), ":-1: Tu es 2ème! Tu as trouvé le bon personnage en "+str(listPlayer[user2ID]['nbTours'])+" tours, alors que "+getUserName(dico['user'])+" a trouvé en "+str(listPlayer[dico['user']]['nbTours'])+" tours")
                            sendMessage(dico['channel'], ":crown: Tu as gagné! Tu as trouvé le bon personnage en "+str(listPlayer[dico['user']]['nbTours'])+" tours, alors que "+user2Name+" a trouvé en "+str(listPlayer[user2ID]['nbTours'])+" tours")
                        else:
                            sendMessage(dico['channel'], ":facepunch:  Egalité! Vous avez tous les 2 trouvé le bon personnage en "+str(listPlayer[dico['user']]['nbTours'])+" tours.")
                            sendMessage(getChannel(user2ID), ":facepunch:  Egalité! Vous avez tous les 2 trouvé le bon personnage en "+str(listPlayer[dico['user']]['nbTours'])+" tours.")

                        del listPlayer[user2ID]
                        del listPlayer[dico['user']]
                else:
                    sendMessage(dico['channel'], "Ce n'est pas le bon personnage!")
                    sendMessage(getChannel(user2ID), user1Name+" s'est trompé de personnage, il pensait à "+list[1])
                    increaseTurn(dico['user'])
            else:
                sendMessage(dico['channel'], "Ce n'est pas le bon moment pour répondre.")
        else:
            sendMessage(dico['channel'], "Erreur: nombre d'arguments invalide (akinator reponse [personnage])")



    if(list[0] == "shutdown"):
        if getUserName(dico['user']) in listAdmin:
            sendMessage(dico['channel'], "Je reviendrai... :ghost: :ghost: :ghost:")
            stop()
        else:
            sendMessage(dico['channel'], "Tu ne peux pas m'arrêter car tu es trop faible :smiling_imp:")


    elif(dico['user'] in listPlayer and dico['channel'] == getChannel(dico['user'])):
        askOrAnswer(dico);


def getUserID(name):
    for u in userList['members']:
        if(u['name'] == name):
            return u['id']
    return None

def getUserName(id):
    for u in userList['members']:
        if(u['id'] == id):
            return u['name']
    return None

def getChannel(userID):
    chan = sc.api_call("im.open", user=userID)
    return chan['channel']['id']

def sendMessage(chan, txt):
    sc.api_call("chat.postMessage", as_user="true", channel=chan, text=txt)

def addGame(player, adversaire, personnage):
    if player in listPlayer or adversaire in listPlayer:
        return False

    addPlayer(player, adversaire, False, personnage)
    addPlayer(adversaire, player, True)

    return True

def addPlayer(player, adversaire, poseQuestion, personnage=None):
    listPlayer[player] = {'adversaire':adversaire, 'poseQuestion':poseQuestion, 'personnage':personnage, 'nbTours':0, 'actif':poseQuestion}

def increaseTurn(userID):
    listPlayer[userID]['nbTours'] = 1 + listPlayer[userID]['nbTours']



if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    loop.set_debug(DEBUG)
   # loop.add_signal_handler(signal.SIGINT, stop)
    loop.run_until_complete(bot(TOKEN))
    loop.close()
