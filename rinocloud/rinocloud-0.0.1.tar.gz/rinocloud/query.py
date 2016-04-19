import rinocloud


class Query():

    OPERATORS = [
        'lt', 'lte', 'gt', 'gte', 'ne', 'in', 'nin', 'exists', 'or'
    ]

    def __init__(self, dictionary={}, results='The query method has not yet been called.'):
        self.dictionary = dictionary
        self.results = results

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
                self.dictionary[attr] = value
            elif operator is 'or':
                option_list = []
                if '$or' in self.dictionary:
                    option_list = self.dictionary['$or']
                    option_list.append({attr: value})
                    self.dictionary['$' + operator] = option_list
                else:
                    option_list.append({attr: value})
                    self.dictionary['$' + operator] = option_list
            else:
                if attr in self.dictionary:
                    self.dictionary[attr]['$' + operator] = value
                else:
                    self.dictionary[attr] = {'$' + operator: value}
        return self

    def print_filter(self):
        print self.dictionary

    def return_filter(self):
        return self.dictionary

    def remove_filter(self, key=None):
        if key is None:
            self.dictionary = {}
        else:
            self.dictionary.pop(key)

    def query(self, **kw):
        r = rinocloud.http.query(self.dictionary)
        assert r.status_code == 200, "Query failed: %s" % r.text
        reply = r.json()["result"]
        return [rinocloud.Object()._process_returned_metadata(item, **kw) for item in reply]
