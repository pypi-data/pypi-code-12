import logging
import xml.etree.ElementTree as ET
from urllib import parse

from osaapi import OSA

from apslite_agent.config import get_config
from apslite_agent.tasks import base

logger = logging.getLogger(__name__)


class HealthCheck(base.Task):
    name = 'health_check'

    def __init__(self, config):
        self.openapi = config.get('openapi', {})
        self.openapi_url = config.get('openapi_url')
        self.rest_url = config.get('rest_url', '')

    def get_full_report(self, p):
        report = p.statistics.getStatisticsReport(reports=[
            {'name': 'report-for-cep', 'value': ''}
        ])

        tree = ET.fromstring(report['result'][0]['value'])

        return {
            'version_oa': tree.find('ClientVersion').text,
        }

    def run(self):
        if not self.openapi:
            return self.result('Error', "Improperly configured")

        logger.info("Querying OpenAPI")
        p = OSA(**self.openapi)
        data = {
            'url_openapi': self.openapi_url,
            'url_rest': self.rest_url,
        }

        try:
            if self.data.get('extended'):
                data.update(self.get_full_report(p))
            else:
                p.getUserByLogin(login='admin')
        except Exception as e:
            logger.warn("OpenAPI call failed")
            return self.result('Error', str(e))

        url = parse.urlparse(self.rest_url)

        logger.info("OpenAPI check succeeded")

        return self.result('OK', data=data)


def task_factory(**kwargs):
    c = get_config()
    oa = c.get('oa', {})

    return {
        HealthCheck.name: HealthCheck(oa)
    }
