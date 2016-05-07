import sys
if sys.version_info < (3, 0):
    from with_test import test, test_case, get_test_self, inject, inject_customized_must_method, only_test, capture_output
else:
    from .with_test import test, test_case, get_test_self, inject, inject_customized_must_method, only_test, capture_output




__author__ = 'Colin Ji'
__versioninfo__ = (2, 0, 2)
__version__ = '.'.join(map(str, __versioninfo__))

__all__ = ['test', 'test_case', 'get_test_self', 'inject', 
        'inject_customized_must_method', 'only_test', 'capture_output']
