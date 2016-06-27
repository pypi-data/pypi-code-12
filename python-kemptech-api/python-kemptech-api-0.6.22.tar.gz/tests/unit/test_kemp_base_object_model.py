from nose.tools import assert_equal

import python_kemptech_api.client as client


class Test_KempBaseObjectModel:

    def test_to_api_dict(self):
        kbo = client.KempBaseObjectModel()
        kbo.ip_address = 'ip'
        kbo.interesting = 'very'
        kbo._ignore_me = 'lalala'

        res = kbo.to_api_dict()
        assert_equal(res, {"interesting": "very"})

    def test_repr(self):
        class MySubclass(client.KempBaseObjectModel):
            pass

        my = MySubclass()
        my.stuff = 'x'
        assert_equal (str(my), "MySubclass {'stuff': 'x'}")
