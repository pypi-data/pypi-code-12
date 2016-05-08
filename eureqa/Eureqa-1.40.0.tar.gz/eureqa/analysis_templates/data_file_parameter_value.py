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


from parameter_value import ParameterValue

import json

class DataFileParameterValue(ParameterValue):
    """Combo box parameter description for analysis template

    :param Eureqa eureqa: A eureqa connection.
    :param str id: The id of the parameter.
    :param str value: The parameter value.
    :param int object_store_bucket: The specific collection in the object store.
    :param str object_store_key: The reference into the object store bucket for this id.

    :var str id: The id of the parameter.
    :var str value: The parameter value.
    """

    def __init__(self, eureqa, id, value, object_store_bucket, object_store_key):
        """Initializes a new instance of the ~DataFileParameterValue class
        """
        ParameterValue.__init__(self, id, value, "data_file")
        self.object_store_bucket = object_store_bucket
        self.object_store_key = object_store_key

    def _to_json(self):
        body = {}
        ParameterValue._to_json(self, body)
        body["objstore_bucket"] = self.object_store_bucket
        body["objstore_key"] = self.object_store_key
        return body

    def __str__(self):
        return json.dumps(self._to_json(), indent=4)

    @staticmethod
    def _from_json(eureqa, body):
        param = DataFileParameterValue(eureqa, None, None, None, None)
        ParameterValue._from_json(param, body)
        param.object_store_bucket = body['objstore_bucket']
        param.object_store_key = body['objstore_key']
        if param._type != "data_file": raise Exception("Invalid type '%s' specified for data file parameter value" % param._type)
        return param

