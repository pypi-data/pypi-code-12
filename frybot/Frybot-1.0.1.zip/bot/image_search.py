"""Image searching function
used to search and send random images to slack channel"""
import json
from random import randrange

import requests

from conf.config import KEY, USER
from bot.debug import print_debug


def search_image(input):
    """
    search_image function
    :param: input
    :return: result url """
    try:
        # search engine initialization
        searchTerm = "Futurama "+input
        startIndex = str(randrange(0, 25))
        key = KEY
        cx = USER
        searchUrl = "https://www.googleapis.com/customsearch/v1?q=" + \
                    searchTerm + "&start=" + startIndex + "&key=" + key + "&cx=" + cx + \
                    "&searchType=image"

        r = requests.get(searchUrl)
        response = r.content.decode('utf-8')
        result = json.loads(response)

        rand_index = randrange(0, 10)
        url = result["items"][rand_index]["link"]

        print_debug(url)
        return url

    except Exception as e:
        print(e)
