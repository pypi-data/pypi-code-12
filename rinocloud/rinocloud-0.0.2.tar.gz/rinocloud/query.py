import rinocloud


class Query():

    OPERATORS = [
        'eq', 'lt', 'lte', 'gt', 'gte', 'ne', 'in', 'nin', 'exists', 'or', 'string_contains'
    ]

    def __init__(self, query_dict={}, results='The query method has not yet been called.'):
        self.query_dict = query_dict
        self.results = results

    def __repr__(self):
        return "<rinocloud.Query>"

    @classmethod
    def extract_filter_operator(cls, parameter):
        for op in cls.OPERATORS:
            underscored = '__%s' % op
            if parameter.endswith(underscored):
                return parameter[:-len(underscored)], op
        return parameter, None

    def filter(self, **kw):
        for name, value in kw.items():
            attr, operator = Query.extract_filter_operator(name)
            if operator is None:
                self.query_dict[attr] = value
            elif operator is 'or':
                option_list = []
                if '$or' in self.query_dict:
                    option_list = self.query_dict['$or']
                    option_list.append({attr: value})
                    self.query_dict['$' + operator] = option_list
                else:
                    option_list.append({attr: value})
                    self.query_dict['$' + operator] = option_list
            else:
                if attr in self.query_dict:
                    self.query_dict[attr]['$' + operator] = value
                else:
                    self.query_dict[attr] = {'$' + operator: value}
        return self

    def query(self, truncate_metadata=True, limit=20, offset=0, **kw):
        r = rinocloud.http.query(self.query_dict, truncate_metadata, limit, offset)
        assert r.status_code == 200, "Query failed: %s" % r.text
        reply = r.json()["result"]
        return [rinocloud.Object()._process_response_metadata(item, **kw) for item in reply]

    def count(self, **kw):
        r = rinocloud.http.count(self.query_dict)
        assert r.status_code == 200, "Query failed: %s" % r.text
        return r.json()["count"]
