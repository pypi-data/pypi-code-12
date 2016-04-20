'''
Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: Apache 2.0, see LICENSE for more details.
'''
from sxclient.defaults import DEFAULT_UPLOADER_BATCH_SIZE
from sxclient.tools.blocks_generator import generate_blocks

__all__ = ['SXFileUploader']


class SXFileUploadContext(object):
    stream = None
    cluster_uuid = None
    block_size = None
    volume = None
    file_size = None
    file_name = None
    meta = None
    data = None
    token = None
    uploaded_blocks = None
    upload_data = None
    initalization_node = None
    number_of_requests = 0

    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            if hasattr(self, key):
                setattr(self, key, value)

    @property
    def data_size(self):
        return len(self.data)


class SXFileUploader(object):
    '''Responsible for file uploads to SX server.'''
    MAX_BATCH_SIZE = DEFAULT_UPLOADER_BATCH_SIZE

    def __init__(self, sxcontroller):
        '''
        Arguments:
          - sxcontroller -- SXController instance.
        '''
        self._sxcontroller = sxcontroller

    def _create_blocks(self, context, blocks):
        block_dict = dict(blocks)
        node_block_dict = {}

        for block_hash, nodes in context.upload_data.iteritems():
            core_node = nodes[0]
            node_block_dict.setdefault(core_node, [])
            node_block_dict[core_node].append(block_hash)

        for node, block_hashes in node_block_dict.iteritems():
            content = ''.join(
                block_dict[block_hash] for block_hash in block_hashes
            )
            self._sxcontroller.createBlocks.call_on_node(
                node,
                context.block_size,
                context.token,
                content
            )
            context.number_of_requests += 1

        context.uploaded_blocks += len(blocks)

    def _upload_context(self, context):
        blocks = generate_blocks(
            context.block_size,
            context.cluster_uuid,
            context.data
        )
        blocks = list(blocks)

        if context.token is None:
            initialize_step = self._upload_initialize_file
        else:
            initialize_step = self._upload_initialize_add_chunk

        initialize_step(context, blocks)
        self._create_blocks(context, blocks)

    def _upload_initialize_file(self, context, blocks):
        response = self._sxcontroller.initializeFile.call(
            context.volume,
            context.file_name,
            context.file_size,
            [block[0] for block in blocks],  # hashes
            context.meta
        )
        context.number_of_requests += 1
        context.initalization_node = response.node_address
        data = response.json()
        context.token = data['uploadToken']
        context.upload_data = data['uploadData']

    def _upload_initialize_add_chunk(self, context, blocks):
        response = self._sxcontroller.initializeAddChunk.call_on_node(
            context.initalization_node,
            context.token,
            context.uploaded_blocks,
            [block[0] for block in blocks],  # hashes
        )
        context.number_of_requests += 1
        context.upload_data = response.json()['uploadData']

    def _flush(self, context):
        self._sxcontroller.flushUploadedFile.call_on_node(
            context.initalization_node,
            context.token
        )
        context.number_of_requests += 1

    def upload_stream(
        self, volume, file_size, file_name, stream, meta={}, before_flush=None
    ):
        '''
        Uploads the file in one go. It is responsible for reading a (file)
        stream, dividing it into appropriate blocks, initializing file/chunks,
        uploading blocks and flushing whole thing at the end.

        Example usage:

            >>> import sxclient
            >>>
            >>> # initialize sx
            >>> cluster = sxclient.Cluster('my.cluster.example.com')
            >>> user_data = sxclient.UserData.from_key_path(
            ...    '/path/to/my/keyfile')
            >>> sxcontroller = sxclient.SXController(cluster, user_data)
            >>> file_uploader = sxclient.SXFileUploader(sxcontroller)
            >>>
            >>> # get file data
            >>> import os
            >>> file_name = 'myfile.txt'
            >>> file_size = os.stat(file_name).st_size
            >>>
            >>> # upload the file
            >>> with open(file_name, 'r') as file_stream:
            ...     file_uploader.upload_stream(
            ...         'my-volume', file_size, 'my_new_file_name.txt',
            ...         file_stream
            ...     )
        '''
        volume_info = self._sxcontroller.locateVolume.json_call(
            volume, size=file_size, includeMeta=True
        )
        volume_filter = volume_info['volumeMeta'].get('filterActive')
        if volume_filter:
            raise NotImplementedError('Volume filters are not supported yet.')

        context = SXFileUploadContext(
            stream=stream,
            cluster_uuid=self._sxcontroller.get_cluster_uuid(),
            block_size=volume_info['blockSize'],
            volume=volume,
            file_size=file_size,
            file_name=file_name,
            meta=meta,
            data='',
            uploaded_blocks=0,
        )

        chunk = stream.read(context.block_size)
        while chunk:
            diff = self.MAX_BATCH_SIZE - (context.data_size + len(chunk))
            if diff == 0:
                context.data += chunk
                self._upload_context(context)
                context.data = ''
            elif diff < 0:
                context.data += chunk[:diff]
                self._upload_context(context)
                context.data = chunk[diff:]
            else:
                context.data += chunk
            chunk = stream.read(context.block_size)

        if context.data or not context.uploaded_blocks:
            self._upload_context(context)
            context.data = ''

        if callable(before_flush):
            before_flush(context)

        self._flush(context)
