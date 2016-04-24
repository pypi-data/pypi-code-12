# pylint: disable=no-self-use
import sets


class TestDiskCache:

    def test_only_called_once(self, tmpdir):
        called = 0
        @sets.disk_cache('foo', prefix=str(tmpdir))
        def pipeline():
            nonlocal called
            called += 1
            return 'Foo'
        assert called == 0
        assert pipeline() == 'Foo'
        assert called == 1
        assert pipeline() == 'Foo'
        assert called == 1

    def test_new_argument(self, tmpdir):
        @sets.disk_cache('foo', prefix=str(tmpdir))
        def pipeline(argument):
            return 2 * argument
        assert pipeline(1) == 2
        assert pipeline(2) == 4

    def test_method_argument(self, tmpdir):
        called = 0
        @sets.disk_cache('foo', method=True, prefix=str(tmpdir))
        def pipeline(self):
            # pylint: disable=unused-argument
            nonlocal called
            called += 1
            return 'Foo'
        assert called == 0
        assert pipeline(None) == 'Foo'
        assert called == 1
        assert pipeline(None) == 'Foo'
        assert called == 1
