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

    def send_product(self, crud, account_id, product_sku, product_dict,
                     version="v1", **kwargs):
        path = 'integration/{}/{}/{}/{}'.format(
            version, crud, account_id, product_sku)

        kwargs.update(json.loads(product_dict))

        method = CRUD_METHODS.get(crud)

        if not method:
            raise ValueError(
                "You need to send a valid CRUD operation:"
                " create, read, update or delete")

        return self.to_dict(path, method=method, meta=True, **kwargs)
