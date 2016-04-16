import logging
import projex.text

from projex.lazymodule import lazy_import
from projex.enum import enum
from ..column import Column

orb = lazy_import('orb')
log = logging.getLogger(__name__)


class ReferenceColumn(Column):
    """
    The ReferenceColumn class type will allow for relational references between models.


    Usage
    ----

        import orb

        class Comment(orb.Table):
            created_by = orb.RelationColumn(reference='User',
                                            reverse=orb.ReferenceColumn.Reversed(name='commments'))

    """
    RemoveAction = enum(
        'DoNothing',    # 1
        'Cascade',      # 2
        'Block'         # 4
    )

    def __json__(self):
        output = super(ReferenceColumn, self).__json__()
        output['reference'] = self.__reference
        output['removeAction'] = self.RemoveAction(self.__removeAction)
        return output

    def __init__(self,
                 reference='',
                 removeAction=RemoveAction.Block,
                 **kwds):
        super(ReferenceColumn, self).__init__(**kwds)

        # store reference options
        self.__reference = reference
        self.__removeAction = removeAction

    def _restore(self, value, context=None):
        if not context.inflated and isinstance(value, orb.Model):
            return value.id()
        elif context.inflated and value is not None:
            model = self.referenceModel()

            if not isinstance(value, model):
                return model.fetch(value)
            else:
                return value
        else:
            return value

    def copy(self):
        out = super(ReferenceColumn, self).copy()
        out.__reference = self.__reference
        out.__removeAction = self.__removeAction
        return out

    def dbType(self, connectionType):
        model = self.referenceModel()
        dbname = model.schema().dbname()
        id_column = model.schema().idColumn()

        if connectionType == 'Postgres':
            if id_column.type() == 'hash':
                return 'character varying({0}) REFERENCES "{1}"'.format(id_column.bits() * 2, dbname)
            else:
                return 'bigint REFERENCES "{0}"'.format(dbname)
        elif connectionType == 'SQLite':
            return id_column.dbType(connectionType)
        else:
            return ''

    def dbRestore(self, db_value, context=None):
        """
        Extracts the db_value provided back from the database.

        :param db_value: <variant>
        :param context: <orb.Context>

        :return: <variant>
        """
        if isinstance(db_value, (str, unicode)) and db_value.startswith('{'):
            try:
                db_value = projex.text.safe_eval(db_value)
            except StandardError:
                log.exception('Invalid reference found')
                raise orb.errors.OrbError('Invalid reference found.')

        if isinstance(db_value, dict):
            cls = self.referenceModel()
            if not cls:
                raise orb.errors.ModelNotFound(self.reference())
            else:
                load_event = orb.events.LoadEvent(data=db_value)

                # update the expansion information to not propagate to references
                if context:
                    context = context.copy()
                    expand = context.expandtree()
                    sub_expand = expand.pop(self.name(), {})
                    context.expand = context.raw_values['expand'] = sub_expand

                db_value = cls(loadEvent=load_event, context=context)

        return super(ReferenceColumn, self).dbRestore(db_value, context=context)

    def loadJSON(self, jdata):
        """
        Loads the given JSON information for this column.

        :param jdata: <dict>
        """
        super(ReferenceColumn, self).loadJSON(jdata)

        # load additional information
        self.__reference = jdata.get('reference') or self.__reference
        self.__removeAction = jdata.get('removeAction') or self.__removeAction

    def random(self):
        """
        Returns a random value that fits this column's parameters.

        :return: <variant>
        """
        return self.referenceModel().schema().idColumn().random()

    def reference(self):
        return self.__reference

    def referenceModel(self):
        """
        Returns the model that this column references.

        :return     <Table> || None
        """
        model = orb.system.model(self.__reference)
        if not model:
            raise orb.errors.ModelNotFound(self.__reference)
        return model

    def restore(self, value, context=None):
        """
        Returns the inflated value state.  This method will match the desired inflated state.

        :param value: <variant>
        :param inflated: <bool>

        :return: <variant>
        """
        context = context or orb.Context()
        value = super(ReferenceColumn, self).restore(value, context=context)

        # check to make sure that we're processing the right values
        if self.testFlag(self.Flags.I18n) and context.locale == 'all':
            return {locale: self._restore(val, context) for locale, val in value.items()}
        else:
            return self._restore(value, context)

    def validate(self, value):
        if isinstance(value, orb.Model) and not isinstance(value, self.referenceModel()):
            raise orb.errors.InvalidReference(self.name(), type(value).__name__, type(self.referenceModel()).__name__)
        else:
            return super(ReferenceColumn, self).validate(value)

# register the column addon
Column.registerAddon('Reference', ReferenceColumn)