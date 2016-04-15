import logging
import ruamel.yaml as yaml

from .base_loader import BaseLoader

logger = logging.getLogger(__name__)


class YAMLLoader(BaseLoader):
    def load_config(self):
        ret = None
        with open(self.filename, 'rb') as fin:
            ret = yaml.load(fin, Loader=yaml.RoundTripLoader) or {}
        return ret

    def save_config(self, config):
        with open(self.filename, 'w') as fout:
            logger.debug('saving config: %s', config)
            yaml.dump(config, fout, indent=2, Dumper=yaml.RoundTripDumper)
