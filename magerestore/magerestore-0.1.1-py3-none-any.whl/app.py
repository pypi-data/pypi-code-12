from magerestore.config import Config
from magerestore.resource import ResourceManager, MagentoDatabaseResource, MagentoMediaResource
from magerestore.repository import RepositoryManager, SFTPRepository


class Magerestore:
    def __init__(self, config_file=None):
        self.config = Config()
        self.config.from_json(config_file)
        self.repo_manager = RepositoryManager(self.config.repos)
        self.repo_manager.factory.add_type('sftp', SFTPRepository)

        self.resource_manager = ResourceManager(self.config.resources, self.repo_manager)
        self.resource_manager.factory.add_type('magento_database', MagentoDatabaseResource)
        self.resource_manager.factory.add_type('magento_media', MagentoMediaResource)
