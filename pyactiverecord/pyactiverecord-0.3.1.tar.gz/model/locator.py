from model.criteria import Criteria as Criteria


class Locator:
    criterias = {}

    @classmethod
    def query(cls, klass):
        if klass.__name__ in cls.criterias:
            return cls.criterias[klass.__name__]

        cls.criterias.update({klass.__name__: Criteria(klass)})
        criteria = cls.criterias[klass.__name__]

        if not criteria.is_exist_table():
            criteria.create()
            return cls.criterias[klass.__name__]

        attributes = klass.attributes(klass)
        diff = klass.difference(attributes)
        for k, v in diff.items():
            if v == "new":
                column = getattr(klass, k)
                klass.add_column(k, column)
            elif v == "deleted":
                klass.delete_column(k)
        return cls.criterias[klass.__name__]