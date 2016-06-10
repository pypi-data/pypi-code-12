import requests as rq
import urllib
import json
from config import Config


class Wunderlist:
    def __init__(self):
        _config_ob = Config()
        self.LIST_ENDPT = "http://a.wunderlist.com/api/v1/lists"
        self.TASK_ENDPT = "http://a.wunderlist.com/api/v1/tasks"
        self.REM_ENDPT = "http://a.wunderlist.com/api/v1/reminders"
        self.config = _config_ob.get_config()
        self.headers = {"X-Client-ID": "059c3e4e19148f6e4bd7",
                        "X-Access-Token": self.config['wl_access_token'],
                        "Content-Type": "application/json"}

        # preload all the lists, reduces latency during taskcreation,..
        self.all_list = json.loads(self.get_all_list().text)

    # Creates a list with the name passed to the function
    def create_list(self, list_name):
        data = {"title": list_name}
        response = rq.post(self.LIST_ENDPT, headers=self.headers,
                           data=json.dumps(data))
        return response

    # Deletes the list with the name
    def delete_list(self, list_name):
        for i in self.all_list:
            if i['title'] == list_name:
                params = {"revision": i['revision']}
                enc_params = urllib.urlencode(params)
                url = self.LIST_ENDPT + "/" + str(i['id']) + "?" + enc_params
                response = rq.delete(url, headers=self.headers)
                return response

    # Returns all the lists
    def get_all_list(self):
        response = rq.get(self.LIST_ENDPT, headers=self.headers)
        return response

    # Creates the specified task under specified list
    def create_task(self, list_id, title, date=None):
        data = {"list_id": list_id, "title": title, "due_date" : date}
        response = rq.post(self.TASK_ENDPT, headers=self.headers,
                           data=json.dumps(data))
        return response

    def list_exists(self, list_name):
        exists = False
        for list in self.all_list:
            if list['title'] == list_name:
                exists = True
                break
        return exists