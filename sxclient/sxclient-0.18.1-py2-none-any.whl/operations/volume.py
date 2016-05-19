'''
Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: Apache 2.0, see LICENSE for more details.
'''
from sxclient.defaults import FILTER_NAME_TO_UUID
from sxclient.operations.base import BaseOperation
from sxclient.models.query_parameters import QueryParameters


__all__ = [
    'ListVolumes', 'LocateVolume', 'CreateVolume', 'ModifyVolume',
    'DeleteVolume'
]


class LocateVolume(BaseOperation):
    '''
    List the VolumeNodes -- nodes responsible for a specific volume.
    Optionally, get additional volume-related data.

    Required access: user with any kind of permissions for the volume.

    Query-specific parameters:
      - volume -- name of the volume to locate
      - size -- parameter used to additionally request correct blocksize for a
        file of 'size' size; if None, blocksize will not be provided
      - includeMeta -- if True, additionally request volume's metadata
      - includeCustomMeta -- if True, additionally request volume's custom
        metadata
    '''

    def _generate_query_params(
        self, volume, size=None, includeMeta=False, includeCustomMeta=False
    ):
        bool_params = set()
        dict_params = {'o': 'locate'}
        if size is not None:
            dict_params['size'] = str(size)
        if includeMeta:
            bool_params.add('volumeMeta')
        if includeCustomMeta:
            bool_params.add('customVolumeMeta')

        return QueryParameters(
            sx_verb='GET',
            path_items=[volume],
            bool_params=bool_params,
            dict_params=dict_params
        )


class ListVolumes(BaseOperation):
    '''
    List all volumes accessible by the user in the cluster.

    Required access: normal.

    Query-specific parameters:
      - includeMeta -- if True, additionally request volumes' metadata
      - includeCustomMeta -- if True, additionally request volumes' custom
        metadata
    '''

    def _generate_query_params(
        self, includeMeta=False, includeCustomMeta=False
    ):
        bool_params = {'volumeList'}
        if includeMeta:
            bool_params.add('volumeMeta')
        if includeCustomMeta:
            bool_params.add('customVolumeMeta')
        return QueryParameters(
            sx_verb='GET',
            bool_params=bool_params
        )


class CreateVolume(BaseOperation):
    '''
    Create a new volume.

    Required access: admin.

    Query specific parameters:
      - volume -- name of the volume to create
      - volumeSize -- size of the new volume
      - owner -- owner of the new volume
      - replicaCount -- number of replicas for the new volume
      - maxRevisions -- maximum number of revisions for each file on the
        volume; if True, it is set to 1
      - volumeMeta -- dictionary containing key-value metadata pairs. The
        values have to be hex-encoded -- with one exception, 'filterActive',
        where it has to be a valid filter name. If None or empty, no metadata
        is set for the volume.
    '''

    def _generate_body(
        self, volume, volumeSize, owner, replicaCount, maxRevisions=None,
        volumeMeta=None
    ):
        body = {
            u'volumeSize': int(volumeSize),
            u'owner': owner,
            u'replicaCount': int(replicaCount)
        }
        if maxRevisions is not None:
            body[u'maxRevisions'] = int(maxRevisions)
        if volumeMeta is not None:
            if u'filterActive' in volumeMeta:
                filter_name = volumeMeta[u'filterActive']
                volumeMeta[u'filterActive'] = FILTER_NAME_TO_UUID[filter_name]

            body[u'volumeMeta'] = volumeMeta
        return body

    def _generate_query_params(
        self, volume, volumeSize, owner, replicaCount, maxRevisions=None,
        volumeMeta=None
    ):
        return QueryParameters(
            sx_verb='JOB_PUT',
            path_items=[volume]
        )


class ModifyVolume(BaseOperation):
    '''
    Modify properties of an existing volume.

    Required access: admin.

    Query specific parameters:
        - volume -- name of the volume to modify
        - size -- new size of the volume; if None, size is not changed
        - owner -- new owner of the volume; if None, owner is not changed
        - newName -- new volume name
        - maxRevisions -- new maximum number of revisions for files on the
          volume; if None, the number is not changed
        - customVolumeMeta -- dictionary containing key-value custom metadata
          pairs. The values have to be hex-encoded. If None or empty, no custom
          metadata is set for the volume.
    '''

    def _generate_body(
        self, volume, size=None, owner=None, newName=None, maxRevisions=None,
        customVolumeMeta=None
    ):
        body = {}
        if size is not None:
            body[u'size'] = int(size)
        if owner is not None:
            body[u'owner'] = owner
        if newName is not None:
            body[u'name'] = newName
        if maxRevisions is not None:
            body[u'maxRevisions'] = int(maxRevisions)
        if customVolumeMeta:
            body[u'customVolumeMeta'] = customVolumeMeta
        return body

    def _generate_query_params(
        self, volume, size=None, owner=None, newName=None, maxRevisions=None,
        customVolumeMeta=None
    ):
        return QueryParameters(
            sx_verb='JOB_PUT',
            path_items=[volume],
            dict_params={'o': 'mod'}
        )


class ChangeVolumeReplica(BaseOperation):
    '''
    Change replica count for a volume.

    Required access: admin.

    Query specific parameters:
        - volume -- name of the volume
        - nextReplica -- value of new volume replica count
    '''

    def _generate_body(self, volume, nextReplica):
        body = {
            u'next_replica': nextReplica,
        }
        return body

    def _generate_query_params(self, volume, nextReplica):
        return QueryParameters(
            sx_verb='JOB_PUT',
            path_items=[volume],
            dict_params={'o': 'replica'}
        )


class DeleteVolume(BaseOperation):
    '''
    Remove a volume.

    Required access: admin.

    Query specific parameters:
        - volume -- name of the volume to delete
        - force -- if set to True, mass delete all the files on the volume
          prior to volume deletion

    Note: cluster doesn't let the removal of volumes containing any files. In
    order to forcibly remove such volume, pass True to the 'force' parameter.
    '''

    def call(self, volume, force=False):
        locate_volume_inst = LocateVolume(self.cluster, self.session)
        response = locate_volume_inst.json_call(volume)
        nodelist = response[u'nodeList']

        if force:
            mass_delete_inst = DeleteVolumeRecursive(
                self.cluster, self.session
            )
            mass_delete_inst.call_on_nodelist(nodelist, volume)

        return self.call_on_nodelist(nodelist, volume)

    def _generate_query_params(self, volume, force=False):
        return QueryParameters(
            sx_verb='JOB_DELETE',
            path_items=[volume]
        )


class DeleteVolumeRecursive(BaseOperation):
    HIDDEN = True

    def _generate_query_params(self, volume):
        return QueryParameters(
            sx_verb='JOB_DELETE',
            path_items=[volume],
            bool_params={'recursive'},
            dict_params={'filter': ''}
        )
