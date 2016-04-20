'''
Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: Apache 2.0, see LICENSE for more details.
'''
import types

from sxclient.exceptions import OperationError
from sxclient.operations.base import VolumeNodeOperation, SingleNodeOperation
from sxclient.models.query_parameters import QueryParameters

__all__ = [
    'GetFile', 'GetFileMeta', 'ListFileRevisions', 'DeleteFile',
    'InitializeFile', 'InitializeAddChunk', 'FlushUploadedFile'
]


class GetFile(VolumeNodeOperation):
    '''
    Retrieves the list of blocks of which a file is comprised of and the nodes
    where those blocks are found.

    Required access: read access

    Query-specific parameters:
      - volume -- the name of the volume
      - path -- the name of the file to retrieve
      - revision -- optional revision of the file
    '''

    def _generate_query_params(self, volume, path, revision=None):
        dict_params = {}
        if revision is not None:
            dict_params['rev'] = revision

        if not path.strip('/'):
            raise OperationError('Invalid file path')

        return QueryParameters(
            sx_verb='GET',
            path_items=[volume, path],
            dict_params=dict_params
        )


class GetFileMeta(VolumeNodeOperation):
    '''
    Retrieves the metadata associated with an existing SX file.

    Required access: read access

    Query-specific parameters:
      - volume -- the name of the volume
      - path -- the name of the file to retrieve its meta
    '''

    def _generate_query_params(self, volume, path):
        return QueryParameters(
            sx_verb='GET',
            path_items=[volume, path],
            bool_params={'fileMeta'}
        )


class ListFileRevisions(VolumeNodeOperation):
    '''
    Retrieves the versions of a given file available on the cluster.

    Required access: read access

    Query-specific parameters:
      - volume -- the name of the volume
      - path -- the name of the file to retrieve its revisions
    '''

    def _generate_query_params(self, volume, path):
        return QueryParameters(
            sx_verb='GET',
            path_items=[volume, path],
            bool_params={'fileRevisions'}
        )


class DeleteFile(VolumeNodeOperation):
    '''
    Delete an existing SX file object.

    Required access: write access

    Query-specific parameters:
      - volume -- the name of the volume
      - path -- the name of the file to delete
    '''

    def _generate_query_params(self, volume, path):
        return QueryParameters(
            sx_verb='JOB_DELETE',
            path_items=[volume, path],
        )


class InitializeFile(VolumeNodeOperation):
    '''
    Initializes the creation of a new file inside an SX volume.

    Note that, after the initialization, the actual file blocks must be
    uploaded with the Create Blocks, and ultimately the file must be flushed
    with the Flush Uploaded File.

    Required access: write access

    Query-specific parameters:
      - volume -- the name of the volume
      - path -- the name of the file to initialize
      - fileSize -- indicates the size in bytes of the file
      - fileData -- contains the sequence of blocks in which the file
        is broken down. Each item is a block name. Note that the block SHA1
        must be salted with the cluster ID.
      - fileMeta -- contains the metadata pairs to set on the file. Metadata
        keys are limited to valid UTF-8 strings; values can be arbitrary
        binary strings and they must be always hex encoded. File metadata
        can only be set at file creation time and can be retrieved via
        the Get File Metadata query.

    Even if under normal circumstances all the file blocks are provided
    at once inside this request, doing so may be impractical for
    extraordinary large files. In such cases Initialize Add Chunk
    adds more blocks to a partially initialized file.
    '''

    def _generate_body(self, volume, path, fileSize, fileData, fileMeta=None):
        assert isinstance(fileData, (list, tuple))
        assert isinstance(fileMeta, (types.NoneType, dict))
        return {
            'fileSize': int(fileSize),
            'fileData': fileData,
            'fileMeta': fileMeta or {},
        }

    def _generate_query_params(
        self, volume, path, fileSize, fileData, fileMeta=None
    ):
        return QueryParameters(
            sx_verb='PUT',
            path_items=[volume, path],
        )


class InitializeAddChunk(SingleNodeOperation):
    '''
    Add more content to an initialized file upload.

    Under normal circumstances all the file content is declared when
    the upload is initialized through the Initialize File query. However,
    whenever doing this is unfeasible or problematic, or when the file is
    really huge, it is possible to declare the file content (i.e. the blocks
    that constitutes it) in sequential steps.

    In order to do so, nothing in the upload process changes, except that
    only the first chunk of blocks appear in the fileData field of
    the initialize request. The subsequent chunks are provided in one or more
    follow-up add chunk requests.

    Although only a minimum of one block per request is currently required,
    for performance reasons it is strongly recommended to generate chunks
    of blocks amounting to about 128MB of file data each. The upload of files
    smaller than that should not make use of this API at all.

    Required access: valid upload token

    Query-specific parameters:
      - node_address -- address of the node to connect to
      - token -- the upload token as received from the Initialize File request.
      - extendSeq -- contains the 0-based sequential block number from which
        the chunk of blocks in fileData starts from. Note: it must always
        match the number of the last block from the previous initialize or
        add chunk operation incremented by one.
      - fileData -- contains the sequence of blocks in that compose the file.
        This is the same as the fileData field in the Initialize File request.
      - fileMeta -- contains the metadata pairs to set on the file.
        This is the same as the fileMeta field in the Initialize File request.
        Note: that the set of metadata declared in each new add chunk request
        merges with the previously declared values. In case of conflict newly
        added values prevail. To remove a previously set key, set its value to
        "null".
    '''

    def _generate_body(self, token, extendSeq, fileData, fileMeta=None):
        assert isinstance(fileData, (list, tuple))
        assert isinstance(fileMeta, (types.NoneType, dict))
        return {
            'extendSeq': int(extendSeq),
            'fileData': fileData,
            'fileMeta': fileMeta or {},
        }

    def _generate_query_params(
        self, token, extendSeq, fileData, fileMeta=None
    ):
        return QueryParameters(
            sx_verb='PUT',
            path_items=['.upload', token],
        )


class FlushUploadedFile(SingleNodeOperation):
    '''
    Finalizes the upload of a file object turning it into existence.

    Note: all the requested file blocks must have been already uploaded
    or this operation will fail.

    Required access: valid upload token

    Query-specific parameters:
      - node_address -- address of the node to connect to
      - token -- the upload token as received from the Initialize File request.
    '''

    def _generate_query_params(self, token):
        return QueryParameters(
            sx_verb='JOB_PUT',
            path_items=['.upload', token],
        )
