from pyramid.httpexceptions import HTTPBadRequest
from pyramid import security

from xbus.monitor.auth import MANAGER_GROUP
from xbus.monitor.resources.root import RootFactory


class GenericRecordFactory(RootFactory):
    """Base factory for individual records; provides:
    - id_attribute: name of the "ID" attribute.
    - record_id.
    - record: sqlalchemy representation of the record.
    - sqla_model: sqlalchemy class.
    - sqla_session: sqlalchemy session object.
    """

    id_attribute = 'id'  # May be overridden by derived classes.
    sqla_model = None  # To be overridden by derived classes.

    # Give managers full access to all models by default. The ACL may be
    # specialized in the derived class.
    __acl__ = [
        (security.Allow, MANAGER_GROUP, 'read'),
        (security.Allow, MANAGER_GROUP, 'update'),
        (security.Allow, MANAGER_GROUP, 'delete'),
    ]

    def __init__(self, request):
        self.record_id = self._get_record_id(request)
        query = self.sqla_session(request).query(self.sqla_model)
        query = query.filter(
            getattr(self.sqla_model, self.id_attribute) == self.record_id
        )
        self.record = query.first()

    def sqla_session(self, request):
        """To be implemented by derived classes.
        :rtype: SQLAlchemy session object.
        """
        raise NotImplementedError

    @staticmethod
    def _get_record_id(request):
        try:
            return request.matchdict.get('id')
        except:
            raise HTTPBadRequest(json_body={"error": "Invalid ID"})
