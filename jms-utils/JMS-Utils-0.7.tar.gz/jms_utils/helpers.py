# --------------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2014-2016 Digital Sapphire
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# --------------------------------------------------------------------------
class EasyAccessDict(object):
    """Provides access to dict by pass a specially made key to
    the get method. Default key sep is "*". Example key would be
    updates*mac*1.7.0 would access {"updates":{"mac":{"1.7.0": "hi there"}}}
    and return "hi there"

    Kwargs:

        dict_ (dict): Dict you would like easy asses to.

        sep (str): Used as a delimiter between keys
    """

    def __init__(self, dict_=None, sep='*'):
        self.sep = sep
        if not isinstance(dict_, dict):
            self.dict = {}
        else:
            self.dict = dict_

    def get(self, key):
        """Retrive value from internal dict.

        args:

            key (str): Key to access value

        Returns:

            (object): Value of key if found or None
        """
        try:
            layers = key.split(self.sep)
            value = self.dict
            for key in layers:
                value = value[key]
            return value
        except KeyError:
            return None
        except Exception as err:  # pragma: no cover
            return None

    # Because I always forget call the get method
    def __call__(self, key):
        return self.get(key)

    def __str__(self):
        return str(self.dict)
