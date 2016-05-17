# external imports
import json
import os
import itertools
from tornado import web
import traitlets
import requests
import datetime
from notebook.services.contents.manager import ContentsManager
# local imports
from .util import _guess_model_type
from .checkpoints import RestfulCheckpoints

class RestfulContentManager(ContentsManager):
    """
        This FileContent Manager handles the retrieval of notebooks from a
        restful api.
    """
    api_endpoint = traitlets.Unicode(
        config=True,
        help="The url endpoint for the remote api."
    )

    request_config = traitlets.Dict(
        help="Configuration for api requests.",
        default_value={},
    )

    def get(self, path, content=True, type=None, format=None):
        """
            This file retrieves the contents for the given filepath from the api
        """
        # figure out the type if we weren't given one
        model_type = type or _guess_model_type(path)
        # make sure the type is valid
        assert model_type in ['notebook', 'directory', 'file'], (
            "Unknown type passed: '{}'".format(type)
        )

        # query the api for the appropriate model
        model = self._query_api_with_model(
            model_type=model_type,
            params=dict(
                path=path.strip('/'),
                format=format
            )
        )

        # if we are looking at a json model and the content is a string
        if model['format'] == 'json' and isinstance(model['content'], str):
            # parse the content as json
            model['content'] = json.loads(model['content'])

        # make sure we have a valid value
        assert model, "File could not be found"

        # if we are supposed to hide the content
        if not content:
            # remove the content related data entries
            model['content'] = None
            model['format'] = None

        return model


    def save(self, model, path=''):
        if 'type' not in model:
            raise web.HTTPError(400, 'No model type provided')
        if 'content' not in model and model['type'] != 'directory':
            raise web.HTTPError(400, 'No file content provided')


        # check that the model type is valid
        if model['type'] not in ('file', 'directory', 'notebook'):
            raise web.HTTPError(400, 'Unhandled model_type: %s' % model['type'])

        # store the path in the model object
        model['path'] = path

        # create the new model through the remote api
        response = self._query_api_with_model(
            model_type=model['type'],
            method='post',
            data=json.dumps(model),
            params=dict(path=path)
        )

        # clear the unneeded data
        response['mimetype'] = None
        response['format'] = None
        response['content'] = None
        response['writable'] = True
        response['name'] = 'foo'
        response['last_modified'] = str(datetime.datetime.now())

        # return the new
        return response


    def delete_file(self, path):
        # send the delete request to the model api
        self._query_api_with_model(
            model_type=_guess_model_type(path),
            method='delete',
            params=dict(path=path)
        )


    def exists(self, path):
        # check if the file or directory exists
        return self.file_exists(path) or self.dir_exists(path)


    def file_exists(self, path):
        # remove any trailing slashes
        model_path = path.strip('/')
        # figure out if the path points to a file or notebook
        model_type = _guess_model_type(path)

        # if the model is not an actual file
        if model_type not in ['file', 'notebook']:
            # then it doesn't exist
            return False

        # check if the appropriate file exists
        return self._check_existence(model_type=model_type, path=model_path)


    def rename_file(self, old_path, new_path):
        print('renaming %s to %s' % (old_path, new_path))
        # send an update to the api that matches the old_dir and sets the new one
        self._query_api_with_model(
            model_type=_guess_model_type(old_path),
            method='post',
            params=dict(path=old_path),
            data=json.dumps(dict(path=new_path))
        )


    def dir_exists(self, path):
        # check if the directory exists
        return self._check_existence(model_type='directory', path=path.strip('/'))


    def is_hidden(self, path):
        return False


    ## Implementation internals


    def _checkpoints_class_default(self):
        return RestfulCheckpoints


    def _check_existence(self, model_type, path):
        # send the delete request to the model api
        response = self._query_api_with_model(
            model_type=model_type,
            params=dict(path=path.strip('/'))
        )
        # if models where retrieved
        if len(response):
            return True
        # otherwise no files were retrieved
        else:
            return False


    def _query_api_with_model(self, model_type, method='get', **kwds):
        """
            This method retrieves the first record matching the arguments
            from the api.
        """
        # add the the ret
        kwds.update(self.request_config)
        print(kwds)
        # parse the remote request as json and return the first entry
        response = getattr(requests, method)(
            self._get_model_endpoint(model_type=model_type),
            **kwds
        )

        try:
            # try to parse the response as json
            return response.json()
        # if the response doesn't contain valid json
        except:
            # return an empty record
            return {}


    def _get_model_endpoint(self, model_type, model_id=None):
        """
            This method generates the api endpoint for the specified model.
        """
        # the url for notebook data
        url = "%s/%s/" % (self.api_endpoint, model_type)
        # if there is a specific model to point to:
        if model_id:
            # add the id to the url
            url += model_id

        # return the url for the model endpoint
        return url
