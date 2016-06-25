import logging

from apslite_agent.config import get_config
from apslite_agent.tasks import base

logger = logging.getLogger(__name__)


class Fake(base.Task):
    name = 'fake'

    def __init__(self, config):
        self.oa_id = config['id']

    def run(self):
        return self.result('OK', data={
            'oa_id': self.oa_id
        })


def task_factory(**kwargs):
    c = get_config()
    oa = c.get('oa', {})

    return {
        Fake.name: Fake(oa)
    }
