from dbs import getDBs, getDBsFromFile
import requests
import json


class rest(object):
    def conn(self):
        if 'dbconffile' in dir(self):
            self.dbs = getDBsFromFile(self.dbconffile)
        else:
            self.dbs = getDBs()

        return self.dbs[self.db]

    def parseQuery(self):
        splits = self.q.split()
        found_select = False
        found_from = False
        found_using = False
        parsed = {
            "select": "",
            "from": "",
            "using": ""
        }
        for word in splits:
            if not found_select:
                if word.strip().lower() == "select":
                    found_select = True
            else:
                if not found_from:
                    if word.strip().lower() == "from":
                        found_from = True
                    else:
                        parsed['select'] += word

                else:
                    if not found_using:
                        if word.strip().lower() == "using":
                            found_using = True
                        else:
                            parsed['from'] += word
                    else:
                        parsed['using'] += word

        parsed['select'] = parsed['select'].split(",")
        parsed['method'] = parsed['using'].split(':')[0]
        parsed['endpoint'] = parsed['using'].split(':')[1]
        return parsed

    def select(self, mydict, path):
        elem = mydict
        try:
            for x in path.strip(".").split("."):
                try:
                    x = int(x)
                    elem = elem[x]
                except ValueError:
                    elem = elem.get(x)
        except:
            pass

        return elem

    def query(self, params):
        conn = self.conn()
        query = self.parseQuery()

        if query['method'].lower() == 'get':
            headers = {conn['header_key']: conn['header_value']}
            print headers
            r = requests.get(conn['base_url'] + query['endpoint'], headers=headers)
            print r.text
            data = r.json()

        lines = []

        for item in self.select(data, query['from']):
            values = []
            for field in query['select']:
                values.append(self.select(item, field))

            lines.append("\t".join(values))

        return lines
