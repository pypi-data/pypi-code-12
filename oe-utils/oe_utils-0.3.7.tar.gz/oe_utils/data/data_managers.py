# -*- coding: utf-8 -*-
from oe_utils.data.data_transfer_objects import ResultDTO


class DataManager(object):
    '''
    A datamanager base class.
    '''

    @staticmethod
    def process_ranged_query(query, result_range):
        '''

        :param query: the query to be processed
        :param result_range: :class: 'oe_utils.range_parser.Range'
        :return: :class:`oe_utils.data.data_transfer_objects.ResultDTO`
        '''
        total = query.count()
        if result_range is not None:
            data = query \
                .offset(result_range.start) \
                .limit(result_range.get_page_size()) \
                .all()
        else:
            data = query.all()
        return ResultDTO(data, total)

    def __init__(self, session, cls):
        '''

        :param session: a db session
        :param cls: the class of the objects to manage
        :return:
        '''
        self.session = session
        self.cls = cls

    def get_one(self, object_id):
        '''
        Retrieve an object by its object_id

        :param object_id: the objects id.
        :return: the requested object
        :raises: :class: NoResultFound when the object could not be found
        '''
        return self.session.query(self.cls).filter_by(id=object_id).one()

    def get(self, object_id, cls=None):
        '''
        Retrieve an object by its object_id

        :param: object_id: the objects id.
        :param: cls: the objects class, if None use the default class from the datamanager
        :return: the requested object or None if not found
        '''
        cls = self.cls if cls is None else cls
        return self.session.query(cls).get(object_id)

    def delete(self, object_id):
        '''
        Delete an object by its id

        :param object_id: the objects id.
        :return: the deleted object
        :raises: :class: NoResultFound when the object could not be found
        '''
        obj = self.session.query(self.cls).filter_by(id=object_id).one()
        self.session.delete(obj)
        return obj

    def save(self, obj):
        '''
        save an object

        :param obj: the object
        :return: the saved object
        '''
        if obj not in self.session:
            self.session.add(obj)
        else:
            obj = self.session.merge(obj)
        self.session.flush()
        self.session.refresh(obj)
        return obj
