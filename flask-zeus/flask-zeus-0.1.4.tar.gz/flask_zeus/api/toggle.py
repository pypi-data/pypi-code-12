from flask_restful import (Resource, marshal)
from flask_login import (login_required, current_user)
from .base import BaseResource
from .errors import *


class ToggleResource(BaseResource, Resource):

    @login_required
    def post(self, **kwargs):
        self.check_model()
        self.check_model_fields()

        if not self.model.has_property('user_id'):
            raise ZeusMethodNotAllowed

        stmt = self.generate_stmt(**kwargs)
        item = stmt.first()

        if not item:
            item = self.model()
            for k, v in kwargs.items():
                if self.model.has_property(k):
                    setattr(item, k, v)
            item.user_id = current_user.id
            item.save()
            return marshal(item, self.model_fields), 201

        item.delete()
        return {}, 204