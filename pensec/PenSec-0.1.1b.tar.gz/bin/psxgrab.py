
import requests
from bs4 import BeautifulSoup
import json


class PSXgrab(object):
    """
    Base class for remote exploit grabber
    """
    def __init__(self):
        self.url = ""

    def search(self, name, category):
        if category not in ['version', 'plugin', 'theme']:
            raise NotImplementedError()


class ExploitDBGrabber(PSXgrab):
    """
    Search sploits on Exploit-db
    """
    def __init__(self):
        self.url = 'https://www.exploit-db.com/search/'

    def search(self, name, category):
        super(ExploitDBGrabber, self).search(name, category)
        name = name.replace("-", " ")
        name = name.replace("_", " ")
        sploits = []
        args = {'action': 'search',
                'text': 'wordpress %s' % name}
        requests.packages.urllib3.disable_warnings()
        response = requests.get(self.url, params=args, verify=False)
        soup = BeautifulSoup(response.text, "lxml")
        exploit_table = soup.find("table", {"class": "exploit_list"})
        if exploit_table is None:
            return sploits
        exploit_data = exploit_table.find("tbody")
        for row in exploit_data.findAll("tr"):
            try:
                date = row.find("td", {'class': 'list_explot_date'}).getText()
                td_class = 'list_explot_description'
                description_cell = row.find("td",
                                            {'class': td_class})
                description = description_cell.find("a").getText()
                link = description_cell.find("a")["href"]
                sploits.append("%s : %s (%s)" % (date, description, link))
            except:
                # Silently pass, parsing html is a pain in the ass
                pass
        return sploits


class WordpressExploitDotComGrabber(PSXgrab):
    """
    Search sploits on wordpressexploits.com
    """
    def __init__(self):
        self.url = 'http://www.wordpressexploit.com/'
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, "lxml")
        self.exploits_rows = soup.findAll('tr', {'class': 'submit'})

    def search(self, name, category):
        super(WordpressExploitDotComGrabber, self).search(name, category)
        name = name.replace("-", " ")
        name = name.replace("_", " ")
        sploits = []
        for row in self.exploits_rows:
            exploit_infos = row.findAll("td")
            try:
                date = exploit_infos[0].getText()
                exploit_name = exploit_infos[1].getText()
                published = exploit_infos[2].getText()
                if "wordpress %s" % name in exploit_name.lower():
                    sploits.append("%s : %s (%s)" % (date,
                                                     exploit_name,
                                                     published))
            except:
                # Silently pass, parsing html is a pain in the ass
                pass
        return sploits


class WpvulndbGrabber(PSXgrab):
    """
    Search sploits on wpvulndb.com
    """
    def __init__(self):
        self.url = 'https://wpvulndb.com/api/v1/'
        self.url_versions = "%s%s" % (self.url, 'wordpresses/')
        self.url_themes = "%s%s" % (self.url, 'themes/')
        self.url_plugins = "%s%s" % (self.url, 'plugins/')

    def search(self, name, category):
        super(WpvulndbGrabber, self).search(name, category)
        sploits = []
        name = name.replace("-", " ")
        name = name.replace("_", " ")
        if category == 'version':
            name = name.replace(".", "")
            full_url = "%s%s" % (self.url_versions, name)
            response = requests.get(full_url)
            if response.status_code == 200:
                json_response = json.loads(response.text)
                for vuln in json_response['wordpress']['vulnerabilities']:
                    url = ""
                    if 'url' in vuln.keys():
                        url = vuln['url'][0]
                    sploits.append("%s : %s (%s)" % (vuln['created_at'],
                                                     vuln['title'],
                                                     url))

        elif category == 'plugin':
            full_url = "%s%s" % (self.url_plugins, name)
            response = requests.get(full_url)
            if response.status_code == 200:
                json_response = json.loads(response.text)
                for vuln in json_response['plugin']['vulnerabilities']:
                    url = ""
                    if 'url' in vuln.keys():
                        url = vuln['url'][0]
                    sploits.append("%s : %s (%s)" % (vuln['created_at'],
                                                     vuln['title'],
                                                     url))

        elif category == 'theme':
            full_url = "%s%s" % (self.url_themes, name)
            response = requests.get(full_url)
            if response.status_code == 200:
                json_response = json.loads(response.text)
                for vuln in json_response['theme']['vulnerabilities']:
                    url = ""
                    if 'url' in vuln.keys():
                        url = vuln['url'][0]
                    sploits.append("%s : %s (%s)" % (vuln['created_at'],
                                                     vuln['title'],
                                                     url))

        return sploits
