
class FieldType(object):
    def __init__(self, field_type_name, field_type):
        self._typ = field_type


class FieldName(object):
    __field_map = {}

    def __init__(self, name, desc, data_type):
        self._name = name
        self._desc = desc
        self._id = self.toid(name)
        self.__class__.__field_map[self._id] = self
        self._data_type = data_type

    def __str__(self):
        return self._name

    def __repr__(self):
        return self._name

    def id(self):
        return self._id

    def description(self):
        return self._desc

    @staticmethod
    def toid(name):
        return ''.join(x for x in name.title() if not x.isspace())

    @classmethod
    def lookup(cls, id):
        return cls.__field_map[id]


# In alphabetical order
ASSET_CLASS = FieldName("Asset Class", "Asset class of a security", str)

COUPON = FieldName("Coupon", "Coupon of a bond in % units", float)
COUPON_FREQ = FieldName("Coupon Frequency", "Coupon frequency of a bond", int)

DAY_COUNT = FieldName("Day Count", "Day count of a security", object)

ISSUE_DATE = FieldName("Issue Date", "Date of issuance of a security", object)

MATURITY_DATE = FieldName("Maturity Date", "Maturity date of a security", object)

PRICE_LAST = FieldName("Price Last", "Last price of a security", float)

SECURITY_TYPE = FieldName("Security Type", "Security Type", str)
SECURITY_SUBTYPE = FieldName("Security Subtype", "Security Subtype", str)

TICKER = FieldName("Ticker", "Ticker identifier for a security", str)
