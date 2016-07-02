from django.db.models.lookups import Exact
from django.db.models import CharField

class CryptoField(CharField):

    def __init__(self, algorithm='bf', *args, **kwargs):
        self.algorithm = algorithm
        self.old_value = None
        super(PGCryptField, self).__init__(*args, **kwargs)

    def value_from_object(self, obj):
        self.old_value = getattr(obj, self.attname)
        return super(PGCryptField, self).value_from_object(obj)

    def get_placeholder(self, value=None, compiler=None, connection=None):
        if value == self.old_value:
            return '%s'

        return "crypt(%s, gen_salt('{0}'))".format(self.algorithm)

    def deconstruct(self):
        name, path, args, kwargs = super(PGCryptField, self).deconstruct()
        if self.algorithm != 'bf':
            kwargs['algorithm'] = self.algorithm
        return name, path, args, kwargs

@CryptoField.register_lookup
class CryptoLookup(Exact):

    def as_sql(self, compiler, connection):
        raise NotImplementedError("Currently on PostgreSQL is available")

    def as_postgresql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)

        params = lhs_params + rhs_params

        return "{0} = crypt({1}, {0})".format(lhs, rhs), params

