from harpoon.errors import UnknownEncryptionType, BadSpecValue

from input_algorithms.dictobj import dictobj
from input_algorithms import spec_base as sb

import six

class PasswordManager(object):
	def __init__(self):
		self.password_types = {}

	def add_password_type(self, typ, decryptor, encryptor):
		self.password_types[typ] = (decryptor, encryptor)

	def resolve(self, typ, val):
		if typ not in self.password_types:
			raise UnknownEncryptionType(wanted=typ, available=list(self.password_types.keys()))
		return self.password_types[typ][0](val)

class Variables(dictobj):
    fields = ["variables"]

    def resolve(self):
        return dict((name, v.resolve()) for name, v in self.variables.items())

class Variable(object):
    def __init__(self, type, value, password_manager):
        self.type = type
        self.value = value
        self.password_manager = password_manager

    def resolve(self):
        if self.type == "plain":
            return self.value
        else:
            return self.password_manager.resolve(self.type, self.value)

class variable_spec(sb.Spec):
    def normalise(self, meta, val):
        password_manager = meta.everything["password_manager"]
        if isinstance(val, six.string_types):
            return Variable("plain", val, password_manager)
        else:
            val = sb.dictionary_spec().normalise(meta, val)
            if len(val) > 1:
                raise BadSpecValue("Expected only one key", got=list(val.keys()))
            return Variable(val.keys()[0], val, password_manager)

passwordable_vars_spec = lambda : sb.container_spec(Variables, sb.dictof(sb.string_spec(), variable_spec()))
