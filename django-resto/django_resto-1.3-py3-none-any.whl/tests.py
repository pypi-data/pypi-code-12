from __future__ import unicode_literals

import django

if django.VERSION[:2] < (1, 6):     # unittest-style discovery isn't available
    from .test_get_setting import SettingsTestCase
    from .test_http_server import HttpServerTestCase
    from .test_regression import RegressionTestCase
    from .test_storage import DistributedStorageTestCase
    from .test_storage import HybridStorageTestCase
    from .test_storage import AsyncStorageTestCase
    from .test_storage import DistributedStorageWithTwoServersTestCase
    from .test_storage import HybridStorageWithTwoServersTestCase
    from .test_storage import AsyncStorageWithTwoServersTestCase
    from .test_storage import DistributedStorageMiscTestCase
    from .test_storage import HybridStorageMiscTestCase
    from .test_storage import AsyncStorageMiscTestCase
