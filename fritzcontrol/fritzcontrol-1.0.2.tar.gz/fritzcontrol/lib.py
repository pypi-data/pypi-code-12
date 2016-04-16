import urllib
import json
import hashlib
import re


# if urllib fails
class NetworkError(Exception):
    pass

# we got redirected to login page


class NotLoggedIn(Exception):
    pass

# credentials are most likely wrong


class WrongCredentials(Exception):
    pass


class FritzControl:

    # builds the urllib request and executes it, returns urrlib obj, wrapper
    def __makeFritzControlRequest(self, urlPart, postData=None):

        # assumes that if post we always need the sid
        if postData:
            postData["sid"] = self.__session_id
        postData = urllib.urlencode(postData)

        url = self.__baseUrl + urlPart + "?sid=" + self.__session_id
        try:
            request = urllib.urlopen(url, postData)
        except:
            raise NetworkError
        if not self.__checkIfLoggedIn(request):
            raise NotLoggedIn
        return request

    # wrapper for __makeFritzControlRequest, ensures we are logged in
    def __fritzControl(self, urlPart, postData=None):
        if self.__session_id is None:
            self.__login()

        try:
            return self.__makeFritzControlRequest(urlPart, postData)
        except NotLoggedIn:
            self.__login()
            return self.__makeFritzControlRequest(urlPart, postData)

    # checks if we are logged in using the redirect url location
    def __checkIfLoggedIn(self, request):
        if "login.lua" in request.geturl():
            return False
        return True

    # there are config/query keys at the end of the html. this is a wrapper for reading it
    def __getConfigValue(self, str, key):

        keyValue = re.findall(r"" + key + ".:.\".+\"", str)
        if not len(keyValue):
            keyValue = re.findall(r"\[\"" + key + "\"\].:.\".+\"", str)
        keyValue = keyValue[0]
        return keyValue.split(":", 1)[1].strip()[1:][:-1]

    def __getSidValue(self, str):

        keyValue = re.findall(r"sid=.+&", str)
        keyValue = keyValue[0]
        return keyValue.split("=", 1)[1].strip()[:-1]

    # login method
    def __login(self):
        def buildPasswordHash(password, challenge):
            password_clean = ''.join([chr if ord(chr) < 255 else 1 for chr in password])
            challenge_password = str(challenge + "-" + password_clean).encode("utf-16le")
            return challenge + "-" + hashlib.md5(challenge_password).hexdigest()

        login_page = urllib.urlopen(self.__baseUrl).read()
        challenge = self.__getConfigValue(login_page, "challenge")
        response = buildPasswordHash(self.__password, challenge)

        loginURL = self.__baseUrl
        postData = urllib.urlencode(
            {"response": response,
             "username": self.__user})
        try:
            loginRequest = urllib.urlopen(loginURL, postData)
        except:
            raise NetworkError

        if not self.__checkIfLoggedIn(loginRequest):
            raise WrongCredentials

        self.__session_id = self.__getSidValue(loginRequest.read())

    def __init__(self, url=None, user=None, password=None, conf=None):

        # default conf path
        if (not url or not user or not password) and not conf:
            conf = "./conf.json"

        # read config file or use params
        if conf:
            with open(conf) as confFile:
                confData = json.load(confFile)
                self.__baseUrl = confData["url"]
                self.__user = confData["user"]
                self.__password = confData["password"]
        else:
            self.__baseUrl = url
            self.__user = user
            self.__password = password
        self.__session_id = None
        # we want a trailing slash for our base url
        if self.__baseUrl[-1] != "/":
            self.__baseUrl += "/"

    # sets our wifi password. only for WPA/WPA2 network now
    def setWifiPassword(self, password):
        self.__fritzControl("wlan/encrypt.lua", {
            "SecLevel": "wpa",
            "wpa_type": "wpamixed",
            "pskvalue": password,
            "wep_type": "128",
            "wepasciivalue": "",
            "WepKey": "0",
            "wephexvalue1": "",
            "wephexvalue2": "",
            "wephexvalue3": "",
            "wephexvalue4": "",
            "wepvalue": "",
            "macfilter": "open",
            "print": "",
            # "validate": "apply",
            "xhr": 1,
            "apply": "",
            "oldpage": "/wlan/encrypt.lua"
        })
