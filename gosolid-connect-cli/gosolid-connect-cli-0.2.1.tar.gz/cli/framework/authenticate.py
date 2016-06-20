# AUTHENTICATION.PY
# This lib is an authentication wrapper that attempts to authenticate by the
# following order of operations:
#   1. Attempt to authenticate by private key stored on system
#   2. If there is no private key / private key is invalid, we ask the user to log in
#   3. User attempts to log in.
#         If the login is successful, we set the secret key and move on
#         If the login is unsuccessful, prompt for username and password again

import requests
import json
import os
import cli.configuration


class Authenticate():
    def __init__(self):
        self.url = cli.configuration.BASE_URL
        self.login_url = self.url + 'user/login'
        self.auth_url = self.url + 'user/authenticate'

        #os agnostic; creates /home/dir/.connect OR C:\Home\Dir\.connect
        self.key_file = os.path.join(os.path.expanduser("~"),".connect")
        self.secret_key = self.get_secret_key()
        self.user_data = None

    #Helper so we don't have to manually parse JSON every time
    @staticmethod
    def request(url, data):
        r = requests.post(url, data=data)
        parsed_reply = json.loads(r.text)
        return parsed_reply

    def login(self):
        # prompt for user and password, make request to Connect
        email = raw_input("Please enter your email: ")
        password = raw_input("Please enter your password: ")
        reply = self.request(self.login_url, {'email': email, 'password': password})
        if reply['success']:
            self.user_data = reply['result']
            #All good - add thank you message, set secret key
            first_name = self.user_data['first_name']
            secret_key = self.user_data['secret_key']
            self.set_secret_key(secret_key)
            print 'Thank you for logging in, %s.' % first_name
            return True
        else:
            # Username and password are wrong - let's get out of here
            print reply['errors'][0]['messages'][0]
            return False

    def get_secret_key(self):
        # Open the secret key file and return key
        # if non-existent or blank, return None
        try:
            with open(self.key_file, 'r+') as f:
                lines = f.readlines()
                if lines[0] == '':
                    return None
                else:
                    return lines[0]
        except IOError:
            return None

    def set_secret_key(self, key):
        #Set the secret key to the key file, flush write buffer
        with open(self.key_file, 'w+') as f:
            f.write(key)
            f.flush()

    def reset_secret_key(self):
        os.remove(self.key_file)

    def authenticate(self):
        if self.secret_key is not None:
            #Make sure that the current authentication key is still valid
            reply = self.request(self.auth_url, {'secret_key': self.secret_key})
            if reply['success']:
                #Move on and do our thing
                self.user_data = reply['result']
                first_name = self.user_data['first_name']
                last_name = self.user_data['last_name']
                print 'Welcome back, %s.' % first_name
                return True
            else:
                #Key is bad - we have to re-authenticate
                self.reset_secret_key()
                print reply['errors'][0]['messages'][0]
                self.login()
        else:
            logged_in = self.login()
            if logged_in:
                return True