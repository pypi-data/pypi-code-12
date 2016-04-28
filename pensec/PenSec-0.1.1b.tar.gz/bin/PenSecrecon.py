

from bs4 import BeautifulSoup
import re
import requests
import random

class PScon():
    def __init__(self, proxy):
        requests.packages.urllib3.disable_warnings()
        self.req = requests.Session()
        self.req.verify = False
        self.version = None
        if proxy is not None:
            self.req.proxies = proxy

    def scan(self, url):
        if not url.endswith('/'):
            url = "%s/" % url

        results = {'printable_results': [],
                   'plugins': []}

        results['printable_results'] = self.get_printable_results(url)
        results['plugins'] = self.get_plugins(url)
        return results

    def get_printable_results(self, url):
        results = {
            'Robots': self.get_robots(url),
            'Readme': self.get_readme(url),
            'Full path disclosure': self.get_fpd(url),
            'Backup': self.get_backup(url),
            'Upload_listing': self.get_upload_listing(url),
            'Version': self.get_version(url),
            'Theme': self.get_theme(url)}
        return results

    def get_user_agent(self):
        user_agents = ["Opera/9.70 (Linux ppc64 ; U; en) Presto/2.2.1"]
        return random.choice(user_agents)

    # Recon methods

    def get_plugins(self, url):
        plugins = []
        headers = {'User-Agent': self.get_user_agent()}
        page_req = self.req.get(url, headers=headers)
        soup = BeautifulSoup(page_req.text, "lxml")

        # Search plugins in css
        plugin_paths = soup.findAll("link", {"rel": "stylesheet"})
        for plugin_path in plugin_paths:
            if 'wp-content/plugins/' in plugin_path['href']:
                regex = re.compile("wp-content/plugins/([a-zA-Z0-9-_]+)/",
                                   re.IGNORECASE)
                r = regex.findall(plugin_path['href'])
                for plugin_name in r:
                    plugins.append(plugin_name)

        # Search plugins in javascript
        plugin_paths = soup.findAll("script",
                                    {"type": "text/javascript"})
        for plugin_path in plugin_paths:
            try:
                if 'wp-content/plugins/' in plugin_path['src']:
                    regex = re.compile("wp-content/plugins/([a-zA-Z0-9-_]+)/",
                                       re.IGNORECASE)
                    r = regex.findall(plugin_path['src'])
                    for plugin_name in r:
                        plugins.append(plugin_name)
            except:
                # Silently pass, parsing html is pain in the ass
                pass

        return list(set(plugins))

    def get_robots(self, url):
        robots = []
        headers = {'User-Agent': self.get_user_agent()}
        full_url = "%s%s" % (url, 'robots.txt')
        robots_req = self.req.get(full_url, headers=headers)
        if robots_req.status_code == 200:
            robots_text = robots_req.text.split("\r\n")
            for robot_text in robots_text:
                if (robot_text.lower().startswith('allow') or
                   robot_text.lower().startswith('disallow')):
                    robots.append(robot_text)
        if not robots:
            return None
        else:
            return robots

    def get_readme(self, url):
        headers = {'User-Agent': self.get_user_agent()}
        full_url = "%s%s" % (url, 'readme.html')
        readme_req = self.req.get(full_url, headers=headers)
        if readme_req.status_code == 200:
            soup = BeautifulSoup(readme_req.text, "lxml")
            version = soup.find("h1").getText().strip()
            self.version = version.replace('Version ', '')
            return full_url
        else:
            return None

    def get_fpd(self, url):
        headers = {'User-Agent': self.get_user_agent()}
        page = 'wp-includes/rss-functions.php'
        full_url = "%s%s" % (url, page)
        fpd_req = self.req.get(full_url, headers=headers)
        if fpd_req.status_code == 200:
            if "Fatal error:" in fpd_req.text:
                return full_url
        return None

    def get_backup(self, url):
        headers = {'User-Agent': self.get_user_agent()}
        backups_find = []
        backups = ["wp-config.php~",
                   "wp-config.php.save",
                   ".wp-config.php.swp",
                   "wp-config.php.swp",
                   "wp-config.php.swo",
                   "wp-config.php_bak",
                   "wp-config.bak",
                   "wp-config.php.bak",
                   "wp-config.save",
                   "wp-config.old",
                   "wp-config.php.old",
                   "wp-config.php.orig",
                   "wp-config.orig",
                   "wp-config.php.original",
                   "wp-config.original",
                   "wp-config.txt"]
        for backup in backups:
            full_url = "%s%s" % (url, backup)
            backup_req = self.req.get(full_url, headers=headers)
            if backup_req.status_code == 200:
                backups_find.append(backup)

        if not backups_find:
            return None
        else:
            return backups_find

    def get_upload_listing(self, url):
        headers = {'User-Agent': self.get_user_agent()}
        full_url = "%s%s" % (url, "/wp-content/uploads/")
        upload_req = self.req.get(full_url, headers=headers)
        if upload_req.status_code == 200:
            if "index of" in upload_req.text.lower():
                return full_url
        return None

    def get_version(self, url):
        if self.version is not None:
            return self.version
        headers = {'User-Agent': self.get_user_agent()}
        page_req = self.req.get(url, headers=headers)
        soup = BeautifulSoup(page_req.text, "lxml")
        generator = soup.find("meta", {'name': 'generator'})
        if generator is not None:
            self.version = generator['content'].replace('Wordpress ',
                                                        '').strip()
        return self.version

    def get_theme(self, url):
        headers = {'User-Agent': self.get_user_agent()}
        page_req = self.req.get(url, headers=headers)
        soup = BeautifulSoup(page_req.text, "lxml")
        theme_paths = soup.findAll("link", {"rel": "stylesheet",
                                            "type": "text/css"})
        for theme_path in theme_paths:
            if 'wp-content/themes/' in theme_path['href']:
                regex = re.compile("wp-content/themes/([a-zA-Z0-9-_]+)/",
                                   re.IGNORECASE)
                r = regex.findall(theme_path['href'])
                if len(r) > 0:
                    return r[0]
        return None
