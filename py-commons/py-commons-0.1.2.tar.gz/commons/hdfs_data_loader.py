import os
import logging

from hdfs import Client


def build_hdfs_client(hdfs_url):
    client = Client(hdfs_url)
    return client


class HDFSFileUploader(object):
    """
    Upload the source file to the target path on HDFS, and overwrites it if exists.

    :type source: string
    :type target_path: string
    :type hdfs_url: string
    """
    def __init__(self, source, target_path, hdfs_url):
        self.client = build_hdfs_client(hdfs_url)
        self.source = source
        self.target_path = target_path

    def __call__(self, data):
        data.to_csv(self.source, sep='\t', index=False, header=False)  # store the output in source path
        self.upload()  # then upload to the HDFS target path

    def upload(self):
        if not os.path.exists(self.source):
            raise ValueError("{source} doesn't exist".format(source=self.source))
        self.client.upload(hdfs_path=self.target_path, local_path=self.source, overwrite=True)
        logging.info("uploaded the file to {path}".format(path=self.target_path))



