# external imports
import requests
import json
from notebook.services.contents.checkpoints import (
    Checkpoints,
    GenericCheckpointsMixin,
)

class RestfulCheckpoints(GenericCheckpointsMixin, Checkpoints):

    def create_notebook_checkpoint(self, nb, path, *args, **kwds):
        """
            Creates a checkpoint out of the current state of the notebook.

            Returns the model for the new checkpoint.
        """
        # add the commit message to the notebook
        commit_message = kwds.pop('commit_message', None)

        # send a request to the api endpoint with the checkpoint
        checkpoint = self._query_api(
            method='post',
            data=json.dumps(nb),
            params=dict(notebook=path, commit_message=commit_message)
        )

        # make sure the id is a string
        checkpoint['id'] = str(checkpoint['id'])

        # return the notebook model
        return checkpoint


    def create_file_checkpoint(self, content, format, path, message):
        """
            Creates a checkpoint out of the current state of the file.

            Returns the model for the new checkpoint.
        """
        # create the file data type
        file = dict(content=content, format=fomat)

        # send a request to the api endpoint with the checkpoint
        checkpoint = self._query_api(
            method='post',
            data=json.dumps(file),
            params=dict(file=path)
        )

        # make sure the id is a string
        checkpoint['id'] = str(checkpoint['id'])

        # return the notebook model
        return checkpoint


    def get_notebook_checkpoint(self, checkpoint_id, path):
        """
            Returns the notebook contents corresponding to the checkpoint_id
            and path.

            Returns a dict of the form:
                {
                    'type': 'notebook',
                    'content': <output of nbformat.read>,
                }
        """
        # return the first entry retrieved by the database with matching id and path
        checkpoint_dict = self._query_api(
            params={
                'id': checkpoint_id,
                'notebook': path
            }
        )[0]

        # add the type to the checkpoint
        checkpoint_dict['type'] = 'notebook'

        # return the augmented checkpoint record
        return checkpoint_dict


    def get_file_checkpoint(self, checkpoint_id, path):
        """
            Returns the file contents corresponding to the checkpoint_id and
            path.

            Returns a dict of the form:
                {
                    'type': 'file',
                    'content': <str>,
                    'format': {'text','base64'},
                }
        """
        # return the first entry retrieved by the database with matching id and path
        checkpoint_dict = self._query_api(
            params={
                'id': checkpoint_id,
                'file': path
            }
        )[0]

        # add the type to the checkpoint
        checkpoint_dict['type'] = 'file'

        # return the augmented checkpoint record
        return checkpoint_dict['content']


    def delete_checkpoint(self, checkpoint_id, path):
        """
            Deletes the checkpoint corresponding to the path and id.
        """
        return self._query_api(
            method='delete',
            params={
                'id': checkpoint_id,
                'path': path
            }
        )


    def list_checkpoints(self, path):
        """
            Lists all of the checkpoints corresponding to the file at the
            given path.

            Returns:
                list(Checkpoint): the checkpoints for the path.
        """
        # return the entries retrieved by the database with matching path
        return self._query_api(params={'path': path})


    def rename_checkpoint(self, checkpoint_id, old_path, new_path):
        """
            Renames the checkpoint with the given id associated with `old_path`
            to point to `new_path`.

            Since the checkpoint/file relation is maintained in a relational
            database, there is no need to rename the checkpoint specifically -
            moving the parent file is enough.
        """


    ## Internals

    def _query_api(self, **kwds):
        """
            Query the remote api to request/mutate checkpoint information.
        """
        return self.parent._query_api_with_model(
            model_type='checkpoint',
            **kwds
        )
