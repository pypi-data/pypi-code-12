from securionpay.resource import Resource


class CrossSaleOffers(Resource):
    def create(self, params):
        return self._post('/cross_sale_offers', params)

    def get(self, cross_sale_offer_id):
        return self._get('/cross_sale_offers/%s' % cross_sale_offer_id)

    def update(self, cross_sale_offer_id, params):
        return self._post('/cross_sale_offers/%s' % cross_sale_offer_id, params)

    def delete(self, cross_sale_offer_id):
        return self._delete('/cross_sale_offers/%s' % cross_sale_offer_id)

    def list(self, params=None):
        return self._get('/cross_sale_offers', params)
