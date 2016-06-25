import logging

import autoupgrade

from apslite_agent.constants import PACKAGE_NAME, PYPI_HOST
from apslite_agent.tasks import base

logger = logging.getLogger(__name__)


class SelfUpgrade(base.Task):
    def __init__(self, consumer):
        self.consumer = consumer
        self.autoupgrade = autoupgrade.AutoUpgrade(
            PACKAGE_NAME,
            index=PYPI_HOST
        )

    def run(self):
        logger.info("Running self-upgrade procedure...")

        if self.autoupgrade.check():
            self.consumer.stop()
            self.autoupgrade.upgrade(dependencies=True)
            self.autoupgrade.restart()

        logger.info("Latest version is already installed")

        return self.result('OK', "Latest version is already installed")


def task_factory(consumer, **kwargs):
    return {
        'self_upgrade': SelfUpgrade(consumer)
    }
