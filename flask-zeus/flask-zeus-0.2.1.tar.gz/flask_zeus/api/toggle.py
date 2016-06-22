from flask_restful import (marshal)
from flask_login import (login_required, current_user)
from .restful import RestfulApi
from .errors import *


class ToggleApi(RestfulApi):

    form = None

    @login_required
    def post(self, **kwargs):
        if not self.model.has_property('user_id'):
            raise ZeusMethodNotAllowed

        stmt = self.get_query(**kwargs)
        item = stmt.first()

        if not item:
            data = kwargs

            if self.form:
                form = self.get_form(self.form, **kwargs)
                if not form.validate_on_submit():
                    raise ZeusBadRequest(details=form.errors)
                data = form.data

            model = self.get_model()
            item = model()
            for k, v in data.items():
                if model.has_property(k):
                    setattr(item, k, v)
            item.user_id = current_user.id
            item.save()
            return marshal(item, self.get_model_fields()), 201

        item.delete()
        return {}, 204
