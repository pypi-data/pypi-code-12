from model.criteria import Criteria as Criteria


class Locator:
    criterias = {}

    @classmethod
    def query(cls, klass):
        if not klass.__name__ in cls.criterias:
            cls.criterias.update({klass.__name__: Criteria(klass)})
            criteria = cls.criterias[klass.__name__]
            if not criteria.is_exist_table():
                criteria.create()
        return cls.criterias[klass.__name__]