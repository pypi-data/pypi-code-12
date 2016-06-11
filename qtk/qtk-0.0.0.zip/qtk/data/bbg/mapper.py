from .. import fields as fl

__field_list_pair = [
    ("BPIPE_REFERENCE_SECURITY_CLASS", fl.ASSET_CLASS),
    ("CPN", fl.COUPON),
    ("CPN_FREQ", fl.COUPON_FREQ),
    ("DAY_CNT_DES", fl.DAY_COUNT),
    ("ISSUE_DT", fl.ISSUE_DATE),
    ("MATURITY", fl.MATURITY_DATE),
    ("PX_LAST", fl.PRICE_LAST),
    ("SECURITY_TYP", fl.SECURITY_TYPE),
    ("SECURITY_TYP2", fl.SECURITY_SUBTYPE)
]

__bbg_to_std = {}
__std_to_bbg = {}

for bbg,std in __field_list_pair:
    __bbg_to_std[bbg] = std
    __std_to_bbg[std] = bbg


def bbg_to_std(key):
    return __bbg_to_std[key]


def std_to_bbg(key):
    return __std_to_bbg[key]

