'''
Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: Apache 2.0, see LICENSE for more details.
'''
__all__ = ['SXFileCat']


class SXFileCat(object):
    '''
    Responsible for file streaming from SX server. It is memory and network
    efficient, at the expense of time. Perfect for streaming small files.
    '''

    def __init__(self, sxcontroller):
        '''
        Arguments:
          - sxcontroller -- SXController instance.
        '''
        self._sxcontroller = sxcontroller

    def initialize(self):
        pass

    def close(self):
        pass

    def __enter__(self):
        self.initialize()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def get_blocks_content_iterator(self, volume, path, revision=None):
        '''
        Downloads the file as a block-by-block iterator.

        Example usage:

            >>> import sxclient
            >>>
            >>> # initialize sx
            >>> cluster = sxclient.Cluster('my.cluster.example.com')
            >>> user_data = sxclient.UserData.from_key_path(
            ...    '/path/to/my/keyfile')
            >>> sxcontroller = sxclient.SXController(cluster, user_data)
            >>> file_downloader = sxclient.SXFileCat(sxcontroller)
            >>>
            >>> # download the file
            >>> blocks = file_downloader.get_blocks_iterator(
            ...    'my_volume', 'my_file')
            >>> for block_content in blocks:
            ...     print block_content
        '''
        volume_info = self._sxcontroller.locateVolume.json_call(
            volume, includeMeta=True
        )
        volume_filter = volume_info['volumeMeta'].get('filterActive')
        if volume_filter:
            raise NotImplementedError('Volume filters are not supported yet.')

        file_info = self._sxcontroller.getFile.json_call(
            volume, path, revision=revision
        )
        block_size = file_info['blockSize']
        amount_to_load = file_info['fileSize']
        file_data = file_info['fileData']

        for block in file_data:
            for block_name, block_nodes in block.iteritems():
                response = self._sxcontroller.getBlocks.call_on_nodelist(
                    block_nodes, block_size, [block_name]
                )
                content = response.content
                amount_to_load -= len(content)
                if amount_to_load < 0:
                    content = content[:amount_to_load]
                    yield content
                    return
                yield content

    def get_file_content(self, volume, path, revision=None):
        '''
        Downloads the file as a whole.

        WARNING: the entire file will be kept in memory so if you are
        dealing with big files use .get_blocks_content_iterator method instead.

        Example usage:

            >>> import sxclient
            >>>
            >>> # initialize sx
            >>> cluster = sxclient.Cluster('my.cluster.example.com')
            >>> user_data = sxclient.UserData.from_key_path(
            ...   '/path/to/my/keyfile')
            >>> sxcontroller = sxclient.SXController(cluster, user_data)
            >>> file_downloader = sxclient.SXFileCat(sxcontroller)
            >>>
            >>> # download the file
            >>> content = file_downloader.get_file_content(
            ...    'my_volume', 'my_file')
            >>> print content
        '''
        return ''.join(
            self.get_blocks_content_iterator(volume, path, revision=revision)
        )
