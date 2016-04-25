import json
import os
import rinocloud


class Object(object):

    def __init__(self, **kw):
        """
        Initialise a bunch of variables
        """
        # these are some rinocloud variables we dont mind showing to the users
        self.id = None
        self.created_on = None
        self.updated_on = None
        self._cloud_name = None
        self.name = None

        # these are some variables we will keep hidden, marked with underscore
        self._size = None
        self._parent = None

        # this needs to be set by the user in order to save locally
        # they just call self.set_local_path
        self._path = rinocloud.path
        self.filepath = ''

        # lets set all the passed kwargs to this object
        for key, value in kw.items():
            setattr(self, key, value)

    def __repr__(self):
        return "<rinocloud.Object name=%s id=%s>" % (self.name, self.id)

    def items(self):
        return self._prep_metadata().items()

    def iteritems(self):
        return self._prep_metadata().items()

    def keys(self):
        return self._prep_metadata().keys()

    def values(self):
        return self._prep_metadata().values()

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __delitem__(self, key):
        del self.__dict__[key]

    def __contains__(self, key):
        return key in self.__dict__

    def __len__(self):
        return len(self.__dict__)

    def view(self):
        return json.dumps(self._prep_metadata(), indent=4)

    def increment_name(self, name, i):
        """
        takes something like
            test.txt
        and returns
            test1.txt
        """
        if i == 0:
            return name
        if '.' in name:
            split = name.split('.')
            split[-2] = split[-2] + str(i)
            return '.'.join(split)
        else:
            return name + str(i)

    def set_name(self, name, overwrite=False, increment=True):
        """
        Sets the name of the file to be saved.

        @params
            name - the name to the file
            increment - whether or not to increment the filename if there is an existing file ie test.txt => test1.txt
            overwrite - whether or not to overwrite existing local file, renders increment redundant
        """

        # check if the file exists
        exists = os.path.exists(os.path.join(self._path, self.increment_name(name, 0)))

        # make sure that we dont overwrite if overwrite and increment are both false
        warning = "Filename and path already exists, refusing to set filename without overwrite=True or increment=True"
        assert not (exists and not overwrite and not increment), warning

        if overwrite is True:
            increment = False

        # otherwise overwrite the file
        if increment is False:
            self.filepath = os.path.join(self._path, self.increment_name(name, 0))
            self.name = self.increment_name(name, 0)
            return self.name

        # or increment the filename
        i = 0
        while os.path.exists(os.path.join(self._path, self.increment_name(name, i))):
            i += 1
        self.name = self.increment_name(name, i)
        self.filepath = os.path.join(self._path, self.increment_name(name, i))
        return self.name

    def set_local_path(self, directory):
        """
            sets path for local saving of information
            if create is true we will create the folder even if it doesnt exist
        """
        self._path = directory

    def _prep_metadata(self):
        # copy the self.__dict__ and delete all that start with _
        obj = self.__dict__.copy()
        [obj.pop(item) for item in list(obj.keys()) if item.startswith('_')]
        # obj.pop('filepath')
        return obj

    def _process_response_metadata(self, response_metadata, **kw):
        self.__dict__.update(response_metadata["metadata"])

        self.id = response_metadata["id"]
        self.created_on = response_metadata["created_on"]
        self.updated_on = response_metadata["updated_on"]
        self._cloud_name = response_metadata["name"]
        self._rino_type = response_metadata["type"]

        if self.name is None:
            self.set_name(response_metadata["name"], **kw)

        # these are some variables we will keep hidden, marked with underscore
        self._size = response_metadata["size"]
        self._parent = response_metadata["parent"]

        return self

    def save_local_metadata(self):
        """
            save all the exposed variables to a json file
        """
        # save to the set local path and add .json
        with open(self.filepath + '.json', 'w+') as outfile:
            json.dump(self._prep_metadata(), outfile, indent=4)

    def import_local_metadata(self):
        with open(self.filepath + '.json', 'r') as infile:
            meta = json.loads(infile.read())
            self.__dict__.update(meta)

    def file_exists(self):
        return os.path.exists(self.filepath)

    def upload(self):
        meta = self._prep_metadata()
        meta["parent"] = self._parent

        if self.file_exists():
            r = rinocloud.http.upload(self.filepath, meta)
        else:
            r = rinocloud.http.upload_meta(meta)

        assert r.status_code == 201, "Upload failed:\n%s" % r.text
        self._process_response_metadata(r.json())

    def upload_meta(self):
        meta = self._prep_metadata()
        meta["parent"] = self._parent
        r = rinocloud.http.upload_meta(meta)
        assert r.status_code == 201, "Upload failed:\n%s" % r.text
        self._process_response_metadata(r.json())

    def update(self):
        meta = self._prep_metadata()
        meta["parent"] = self._parent
        r = rinocloud.http.upload_meta(meta)
        assert r.status_code == 201, "Upload failed:\n%s" % r.text
        self._process_response_metadata(r.json())

    def get(self, id=None, truncate_metadata=True, **kw):
        _id = id
        if _id is None:
            if self.id is None:
                raise AttributeError("Can't fetch without an id. Need to either set Object.id or pass id to get.")
            else:
                _id = self.id

        r = rinocloud.http.get_metadata(_id, truncate_metadata=True)
        assert r.status_code != 404, "Object does not exist in Rinocloud. Error 404."
        self._process_response_metadata(r.json(), **kw)

    def download(self):
        assert self.id is not None, "Need to have id set to download data."
        assert self._rino_type == "file", "Target object is not a file, its a folder or empty object."

        r = rinocloud.http.download(self.id, self.filepath, self._size)
        assert r.status_code == 200, "Download error occured: %s" % r.text
        return self.filepath
