import googleads
from dbs import getDBs, getDBsFromFile
import json


class adwords(object):
    def conn(self):
        if 'dbconffile' in dir(self):
            self.dbs = getDBsFromFile(self.dbconffile)
        else:
            self.dbs = getDBs()

        developer_token = self.dbs[self.db]['developer_token']
        client_customer_id = self.dbs[self.db]['client_customer_id']
        client_secret = self.dbs[self.db]['client_secret']
        refresh_token = self.dbs[self.db]['refresh_token']
        client_id = self.dbs[self.db]['client_id']
        mcc_client_id = self.dbs[self.db]['mcc_client_id']

        auth = googleads.oauth2.GoogleRefreshTokenClient(client_id, client_secret, refresh_token)
        adwords_client = googleads.adwords.AdWordsClient(developer_token, auth, "")
        adwords_client.SetClientCustomerId(mcc_client_id)

        return adwords_client.GetReportDownloader(version='v201509')

    def query(self, params):
        conn = self.conn()

        query_dict = {}
        for i in range(len(self.params)):
            query_dict[self.params[i]] = params[i]

        report_query = (self.q.format(**query_dict))

        result = conn.DownloadReportAsStringWithAwql(report_query, 'TSV', None, True)

        return result.split("\n")
