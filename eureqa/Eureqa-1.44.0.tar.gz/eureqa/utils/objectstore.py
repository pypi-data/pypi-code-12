# Copyright (c) 2016, Nutonian Inc
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the Nutonian Inc nor the
#     names of its contributors may be used to endorse or promote products
#     derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL NUTONIAN INC BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

class ObjectStore:
    """For internal use only. Used to get/put/delete objects from the object store.
    
    :param Eureqa eureqa: a eureqa connection
    """

    def __init__(self, eureqa):
        self._session = eureqa._session

    _uri_root = '/objstore'

    @classmethod
    def get_uri_parts(cls, uri):
        """Given a uri of the form /this/is/a/uri, return a list of the uri components.

        :param obj cls: Classmethod object
        :param str uri: The URI to process.
        :return: a list of the uri components
        :rtype: list
        """

        return uri.split('/')

    @classmethod
    def construct_uri(cls, bucket, key=None):
        """Given a bucket and optional key, construct the objectstore uri
        associated with those values.

        :param obj cls: Classmethod object
        :param str bucket: Objectstore logical container
        :param str key: Objectstore key
        :return: the objectstore uri associated with the specified bucket/key
        :rtype: str
        """

        parts = [cls._uri_root, bucket]
        if key is not None: parts.append(key)
        return '/'.join(parts)

    @classmethod
    def construct_uri_full(cls, organization, bucket, key=None, download=False):
        """Given an organization, bucket and optional key, construct the absolute uri
        associated with those values, starting with '/api'.
        This uri will be accessible from a Web browser.  It may not work from Python.

        :param obj cls: Classmethod object
        :param str organization: The logical organization containing the data.
        :param str bucket: Objectstore logical container
        :param str key: Objectstore key
        :param bool download: Whether to enable download from this URI
        :return: the full objectstore uri associated with the specified bucket/key
        :rtype: str
        """

        uri = cls.construct_uri(bucket, key)
        uri_full = '/api/' + organization + uri
        if download: uri_full += '?download=true'
        return uri_full

    @classmethod
    def construct_python_uri_full(cls, organization, bucket, key=None, download=False):
        """Given an organization, bucket and optional key, construct the absolute uri
        associated with those values, starting with '/api/v2'.
        This uri will be accessible from a python.  It may not work from a Web browser.

        :param obj cls: Classmethod object
        :param str organization: The logical organization containing the data.
        :param str bucket: Objectstore logical container
        :param str key: Objectstore key
        :param bool download: Whether to enable download from this URI
        :return: the full objectstore uri associated with the specified bucket/key
        :rtype: str
        """
        uri = cls.construct_uri(bucket, key)
        uri_full = '/api/v2/' + organization + uri
        if download: uri_full += '?download=true'
        return uri_full

    def get(self, bucket, key=None, filepath=None):
        """Get an object from a bucket/key in the objectstore.

        If no key is specified, the response will be a list of keys in the
        specified bucket

        If filename is specified, result is also saved to file.

        :param str bucket: Objectstore logical container
        :param str key: Objectstore key
        :param str filepath: The (optional) key for this data URI 
        :return: the contents of the bucket/key
        :rtype: str
        """

        uri = self.construct_uri(bucket, key)

        response = self._session.execute(uri, 'GET', raw_returnfile=filepath)
        return response

    def put(self, bucket, key=None, raw_data=None, filepath=None):
        """Put contents into a bucket/key.

        If a key is specified, we'll overwrite the stored value for the
        bucket/key. Otherwise we'll create a new key in the bucket.

        :param str bucket: Objectstore logical container
        :param str key: Objectstore key
        :param bool raw_data: The raw data if provided
        :param str filepath: The filepath if desired
        :return: the response from the objectstore
        :rtype: str
        """

        uri = self.construct_uri(bucket, key)
        files = {'file':open(filepath, 'rb')} if filepath else None
        response = self._session.execute(uri, 'POST', raw_data=raw_data, files=files)
        if files: files['file'].close()
        return response

    def delete(self, bucket, key=None):
        """Delete contents of a bucket or key.

        If no key is specified, we'll delete the entire bucket.

        :param str bucket: Objectstore logical container
        :param str key: Objectstore key
        """

        uri = self.construct_uri(bucket, key)
        response = self._session.execute(uri, 'DELETE')
        return response

