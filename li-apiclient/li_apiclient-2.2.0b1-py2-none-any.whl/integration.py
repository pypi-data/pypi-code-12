# -*- coding: utf-8 -*-
from li_api_client.utils import ApiClientBase

CRUD_METHODS = {
	"create": "POST",
	"read": "GET",
	"update": "PUT",
	"delete": "DELETE"
}

class ApiIntegration(ApiClientBase):
    NOME = "API_INTEGRATION"
    AUTENTICA_APLICACAO = True

    def send_product(self, version="v1", crud, account_id, product_sku, **kwargs):
        path = 'integration/{}/{}/{}/{}'.format(version, crud, account_id, product_sku)
        
        method = CRUD_METHODS.get(crud)

        if not method:
        	raise ValueError("You need to send a valid CRUD operation: create, read, update or delete")

        return self.to_dict(path, method=method, meta=True, **kwargs)