# -*- coding: utf-8 -*-
import json
from li_api_client.utils import ApiClientBase

CRUD_METHODS = {
    "create": "post",
    "read": "get",
    "update": "put",
    "delete": "delete"
}


class ApiIntegration(ApiClientBase):
    NOME = "API_INTEGRATION"
    AUTENTICA_APLICACAO = True

    def send_notification(self, crud, history_id, model_dict,
                          version="v1", **kwargs):
        path = 'integration/{}/{}/{}'.format(
            version, crud, history_id)

        kwargs.update(json.loads(model_dict))

        method = CRUD_METHODS.get(crud)

        if not method:
            raise ValueError(
                "You need to send a valid CRUD operation:"
                " create, read, update or delete")

        return self.to_dict(path, method=method, meta=True, **kwargs)
