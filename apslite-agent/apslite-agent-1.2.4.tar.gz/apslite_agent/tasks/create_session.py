import logging

from osaapi import OSA
import requests

from apslite_agent.config import get_config
from apslite_agent.tasks import base

logger = logging.getLogger(__name__)


class CreateSession(base.Task):
    name = 'create_session'

    def __init__(self, config):
        self.openapi = config.get('openapi', {})
        self.rest_url = config.get('rest_url', '')

    def run(self):
        if not self.openapi:
            return self.result('Error', "Improperly configured")

        if self.data.get('version'):
            logger.info("Set account CCP account_id - %s version - %s",
                        self.data.get('account_id'),
                        self.data.get('version'))

            api = OSA(**self.openapi)
            ret = api.am.setAccountCCPVersion(
                account_id=self.data.get('account_id'),
                ccp_version=self.data.get('version')
            )

            logger.info("result set version - %s", ret)

            if 'error' in ret or ('status' in ret and ret['status'] != 0):
                error_message = ret['message'] if 'message' in ret else 'Error'
                return self.result('Error', error_message)

        url = 'http://{host}:{port}{url}'.format(
            host=self.openapi.get('host'),
            port=8080,
            url=self.data.get('url')
        )

        try:
            logger.info("Request to create OA session")
            res = requests.post(url, timeout=20, verify=False)
            session_id = res.content.decode('utf-8').split('=')[1].replace('\n', '')
            logger.info("Created OA session - %s", session_id)
        except Exception as e:
            logger.exception("Failed to create session")
            try:
                logger.debug("Response from OA: %s", res.content)
            except:
                pass
            return self.result('Error', str(e))

        return self.result('OK', data={
            'session_id': session_id
        })


def task_factory(**kwargs):
    c = get_config()
    oa = c.get('oa', {})

    return {
        CreateSession.name: CreateSession(oa)
    }
