from scrapy.extensions.feedexport import BlockingFeedStorage
from azure.storage.blob import BlockBlobService

from urllib.parse import urlparse


class AzureBlobFeedStorage(BlockingFeedStorage):

    def __init__(self, uri):
        from scrapy.conf import settings
        self.account_name = settings['AZURE_ACCOUNT_NAME']
        self.account_key = settings['AZURE_ACCOUNT_KEY']
        self.container = settings['AZURE_CONTAINER']

        self.filename = settings['AZURE_FILENAME']
        self.blob_service = BlockBlobService(account_name=self.account_name, account_key=self.account_key)

    def _store_in_thread(self, file):
        file.seek(0)
        self.blob_service.create_blob_from_stream( self.container, self.filename, file)
