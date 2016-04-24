import re
from urllib import quote
from random import shuffle
from thespian.actors import *
import requests


class Main(Actor):
    def receiveMessage(self, msg, sender):
        # catch the shutdown request and exit
        if isinstance(msg, ActorExitRequest):
            return None

        # if no command is specified provide some help
        if isinstance(msg, list) and len(msg) == 0:
            self.send(sender, 'usage: dlbot example [text|gif|commit|youtube]')

        # for the command 'text' send back a simple text reply
        elif msg[0] == 'text':
            self.send(sender, 'An example text reply')

        # for the command 'gif' do an image search
        elif msg[0] == 'gif':
            if len(msg) == 1:
                self.send(sender, 'specify an image to search for')
            else:
                searchterm = quote(' '.join(msg[1:]))
                safe = "&safe=active"
                searchurl = "https://www.google.com/search?tbs=itp:animated&tbm=isch&q={0}{1}".format(searchterm, safe)
                useragent = "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_0 like Mac OS X; en-us) AppleWebKit/532.9 (KHTML, like Gecko) Versio  n/4.0.5 Mobile/8A293 Safari/6531.22.7"
                result = requests.get(searchurl, headers={"User-agent": useragent}).text
                def unescape(url): return url.replace(r"\x", "%")
                gifs = list(map(unescape, re.findall(r"var u='(.*?)'", result)))
                shuffle(gifs)
                self.send(sender, gifs[0].encode("utf8"))

        # for the command 'commit' return a funny commit message to use
        elif msg[0] == 'commit':
            self.send(sender, requests.get("http://whatthecommit.com/index.txt").text)

        # for the command 'youtube' return a youtube video
        elif msg[0] == 'youtube':
            if len(msg) == 1:
                self.send(sender, 'specify a video to search for')
            else:
                url = "https://www.youtube.com/results?search_query={0}"
                url = url.format(quote(' '.join(msg[1:])))
                r = requests.get(url)
                results = re.findall('a href="(/watch[^&]*?)"', r.text)
                if not results:
                    self.send(sender, "sorry, no videos found")
                else:
                    self.send(sender, "https://www.youtube.com{0}".format(results[0]))

        # if no commands were recognised
        else:
            self.send(sender, 'unknown example command')

