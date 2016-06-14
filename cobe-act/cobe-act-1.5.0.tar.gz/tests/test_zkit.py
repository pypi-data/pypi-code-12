import threading
import time
import warnings

import pytest
import zmq

import act


@pytest.fixture(autouse=True)
def _enable_warnings():
    """Enable all warnings.

    By default python 3.2 and above suppress some warnings like
    DeprecationWarning.  But we want to test these warnings and
    enabling all warnings during tests is a good idea.
    """
    warnings.resetwarnings()


@pytest.fixture
def ctx(request):
    """A context suitable for tests.

    This automatically sets LINGER to 0 and adds finalisers to
    close any sockets created.  Additionally a :meth:`sockpair`
    method is added to easily return a connected socket pair.
    """
    class Context(zmq.Context):
        _counter = 0        # Stop __getattr__ from grabbing this.

        def __init__(self):
            self._counter = 0
            super().__init__()

        def socket(self, stype):
            sock = super().socket(stype)
            request.addfinalizer(sock.close)
            return sock

        def sockpair(self):
            """Return a connected ``(src, dst)`` socket pair."""
            dst = self.socket(zmq.PAIR)
            src = self.socket(zmq.PAIR)
            endpoint = 'inproc://sockpair/{}'.format(self._counter)
            self._counter += 1
            dst.bind(endpoint)
            src.connect(endpoint)
            return src, dst

    ctx = Context()
    ctx.IPV6 = True   # pylint: disable=attribute-defined-outside-init
    ctx.LINGER = 0    # pylint: disable=attribute-defined-outside-init
    request.addfinalizer(ctx.term)
    return ctx


class TestContext:

    def test_context(self):
        ctx = act.zkit.new_context()
        assert isinstance(ctx, zmq.Context)

    def test_ipv6(self):
        ctx = act.zkit.new_context()
        assert ctx.IPV6 is True

    def test_linger(self):
        ctx = act.zkit.new_context()
        assert 0 < ctx.LINGER < 3000


class TestTimerABC:

    @pytest.fixture
    def timer(self):
        """A simple static timer.

        Initialise with the value, it never counts down.  Initialise
        with ``None`` to set in inactive.
        """
        class Timer(act.zkit.TimerABC):

            def __init__(self, when):
                if when is None:
                    self._active = False
                else:
                    self._active = True
                self._when = when

            @property
            def active(self):
                return self._active

            @property
            def when(self):
                if not self._active:
                    raise ValueError('Not active')
                return self._when

            def cancel(self):
                self._active = False

        return Timer

    def test_active(self, timer):
        assert timer(5).active

    def test_when(self, timer):
        assert timer(5).when == 5

    def test_cancel_active(self, timer):
        t = timer(5)
        assert t.active
        t.cancel()
        assert not t.active

    def test_cancel_when(self, timer):
        t = timer(5)
        assert t.when
        t.cancel()
        with pytest.raises(ValueError):
            t.when              # pylint: disable=pointless-statement

    def test_time_type(self, timer):
        t = timer._time()
        assert isinstance(t, int)

    def test_time_miliseconds(self, timer):
        t1 = timer._time()
        time.sleep(0.002)
        t2 = timer._time()
        assert 0 < t2 - t1 < 10

    def test_obj_eq(self, timer):
        t = timer(5)
        assert t is t

    def test_obj_ne(self, timer):
        t1 = timer(5)
        t2 = timer(5)
        assert t1 is not t2

    @pytest.mark.parametrize(('a', 'b'), [(5, 5),
                                          (None, None)])
    def test_eq(self, timer, a, b):
        t1 = timer(a)
        t2 = timer(b)
        assert t1 == t1
        assert t2 == t2
        assert not t1 == t2

    def test_eq_other(self, timer):
        t = timer(5)
        o = object()
        assert not t == o

    @pytest.mark.parametrize(('a', 'b'), [(5, 6),
                                          (None, 6),
                                          (5, None)])
    def test_ne(self, timer, a, b):
        t1 = timer(a)
        t2 = timer(b)
        assert t1 != t2
        assert not t1 != t1
        assert not t2 != t2

    def test_ne_other(self, timer):
        t = timer(5)
        o = object()
        assert t != o

    @pytest.mark.parametrize(('a', 'b'), [(5, 6),
                                          (5, None)])
    def test_lt(self, timer, a, b):
        t1 = timer(a)
        t2 = timer(b)
        assert t1 < t2
        assert not t2 < t1

    def test_lt_other(self, timer):
        t = timer(5)
        o = object()
        with pytest.raises(TypeError):
            t < o               # pylint: disable=pointless-statement

    @pytest.mark.parametrize(('a', 'b'), [(5, 6),
                                          (5, None),
                                          (None, None)])
    def test_le(self, timer, a, b):
        t1 = timer(a)
        t2 = timer(a)
        t3 = timer(b)
        assert t1 <= t2
        assert t1 <= t3
        assert t2 <= t1

    def test_le_other(self, timer):
        t = timer(5)
        o = object()
        with pytest.raises(TypeError):
            t <= o              # pylint: disable=pointless-statement

    @pytest.mark.parametrize(('a', 'b'), [(5, 6),
                                          (5, None)])
    def test_gt(self, timer, a, b):
        t1 = timer(a)
        t2 = timer(b)
        assert t2 > t1
        assert not t1 > t1

    def test_gt_other(self, timer):
        t = timer(5)
        o = object()
        with pytest.raises(TypeError):
            t > o               # pylint: disable=pointless-statement

    @pytest.mark.parametrize(('a', 'b'), [(5, 6),
                                          (5, None),
                                          (None, None)])
    def test_ge(self, timer, a, b):
        t1 = timer(a)
        t2 = timer(a)
        t3 = timer(b)
        assert t2 >= t1
        assert t3 >= t1
        assert t1 >= t2

    def test_ge_other(self, timer):
        t = timer(5)
        o = object()
        with pytest.raises(TypeError):
            t >= o              # pylint: disable=pointless-statement

    def test_hash(self, timer):
        t = timer(5)
        assert hash(t)


class TestSimpleTimer:

    @pytest.fixture
    def timer(self):
        return act.zkit.SimpleTimer()

    def test_abc(self, timer):
        assert isinstance(timer, act.zkit.TimerABC)

    def test_unscheduled(self, timer):
        with pytest.raises(ValueError):
            assert timer.when

    def test_schedule(self, timer):
        timer.schedule(300)
        assert timer.when > 290 <= 300

    def test_schedule_overwrite(self, timer):
        timer.schedule(300)
        assert timer.when < 600
        timer.schedule(900)
        assert timer.when > 600

    def test_cancel(self, timer):
        timer.schedule(300)
        assert timer.active
        assert timer.when
        timer.cancel()
        assert not timer.active
        with pytest.raises(ValueError):
            assert timer.when

    def test_cancel_unscheduled(self, timer):
        timer.cancel()
        assert not timer.active
        with pytest.raises(ValueError):
            assert timer.when


class TestEventStream:

    @pytest.fixture
    def stream(self, request, ctx):
        stream = act.zkit.EventStream(ctx)
        request.addfinalizer(stream.close)
        return stream

    def test_single_sock_pollin(self, ctx, stream):
        src, dst = ctx.sockpair()
        src.send(b'foo')
        src.send(b'end')
        stream.register(dst, zmq.POLLIN)
        for sock, evt in stream:
            assert evt == zmq.POLLIN
            assert sock is dst
            msg = sock.recv()
            if msg == b'end':
                stream.close()

    def test_multiple_sock_pollout(self, ctx, stream):
        src, dst = ctx.sockpair()
        src.SNDHWM = 3
        dst.RCVHWM = 3
        count = 0
        while src.poll(timeout=1, flags=zmq.POLLOUT):
            src.send(b'foo')
            count += 1
        stream.register(src, zmq.POLLOUT)
        stream.register(dst, zmq.POLLIN)
        for sock, evt in stream:
            if evt == zmq.POLLIN:
                assert sock is dst
                assert count > 0
                sock.recv()
                count -= 1
            else:
                assert sock is src
                stream.close()

    def test_register_invalid_bitmask(self, stream, ctx):
        src, dst = ctx.sockpair()
        with pytest.raises(ValueError):
            stream.register(dst, stream.POLLIN | stream.TIMER)
        with pytest.raises(ValueError):
            stream.register(src, stream.POLLOUT | stream.TIMER)

    def test_unregister(self, ctx, stream):
        src, dst = ctx.sockpair()
        src.send(b'msg')
        stream.register(src, zmq.POLLOUT)
        stream.register(dst, zmq.POLLIN)
        for sock, _ in stream:
            if sock is dst:
                msg = sock.recv()
                if msg == b'end':
                    stream.close()
            if sock is src:
                stream.unregister(src)
                src.send(b'end')
        with pytest.raises(LookupError):
            stream.unregister(src)

    def test_poll_ready(self, ctx, stream):
        src, dst = ctx.sockpair()
        src.send(b'msg')
        stream.register(dst, zmq.POLLIN)
        assert stream.poll(3000)

    def test_poll_wait(self, ctx, stream):
        _, dst = ctx.sockpair()
        stream.register(dst, zmq.POLLIN)
        assert not stream.poll(10)

    def test_poll_closed(self, ctx):
        stream = act.zkit.EventStream(ctx)
        stream.send_term()
        assert stream.poll(0) is True
        for _ in stream:
            pytest.fail('Stream not closed')

    def test_poll_infinite(self, stream):
        assert not stream.poll(10)  # avoid infinite hang

    def test_poll_timer_notimeout(self, stream):
        timer = act.zkit.SimpleTimer()
        stream.register(timer, stream.TIMER)
        timer.schedule(10)
        assert stream.poll()

    def test_poll_notimer_notimeout(self, ctx, stream):
        src, dst = ctx.sockpair()
        stream.register(dst, zmq.POLLIN)
        def send():
            src.send(b'msg')
        timer = threading.Timer(0.05, send)
        timer.start()
        assert stream.poll()

    def test_closed_attr(self, ctx):
        stream = act.zkit.EventStream(ctx)
        assert not stream.closed
        stream.send_term()
        for _ in stream:
            pytest.fail('Stream not closed')
        assert stream.closed

    def test_event_attrs(self, stream):
        assert stream.POLLIN == zmq.POLLIN
        assert stream.POLLOUT == zmq.POLLOUT

    def test_next(self, ctx, stream):
        src, dst = ctx.sockpair()
        src.send(b'msg')
        stream.register(dst, zmq.POLLIN)
        assert stream.poll(3000)
        assert next(stream) == (dst, stream.POLLIN)

    def test_multiple_term(self, ctx):
        stream = act.zkit.EventStream(ctx)
        stream.send_term()
        stream.send_term()
        for _ in stream:
            pytest.fail('Stream not closed')
        assert stream.closed
        stream.send_term()

    def test_multiple_stopiterations(self, ctx):
        stream = act.zkit.EventStream(ctx)
        stream.send_term()
        for _ in stream:
            pytest.fail('Stream not closed')
        for _ in stream:
            pytest.fail('Stream not closed')

    def test_events_queued(self, ctx, stream):
        src0, dst0 = ctx.sockpair()
        src0.send(b'msg')
        src1, dst1 = ctx.sockpair()
        src1.send(b'msg')
        stream.register(dst0, stream.POLLIN)
        stream.register(dst1, stream.POLLIN)
        assert not stream._queued_events
        assert stream.poll(10), 'No event ready'
        event = next(stream)
        assert event[0] in [dst0, dst1]
        assert event[1] == stream.POLLIN
        assert stream._queued_events
        assert stream.poll(0)

    def test_events_queued_unregister(self, ctx, stream):
        src0, dst0 = ctx.sockpair()
        src0.send(b'msg')
        src1, dst1 = ctx.sockpair()
        src1.send(b'msg')
        stream.register(dst0, stream.POLLIN)
        stream.register(dst1, stream.POLLIN)
        assert not stream._queued_events
        assert stream.poll(10), 'No event ready'
        next(stream)
        assert stream._queued_events
        stream.unregister(dst0)
        stream.unregister(dst1)
        assert not stream._queued_events

    def test_multiple_sockets(self, request, ctx):
        src0, dst0 = ctx.sockpair()
        src1, dst1 = ctx.sockpair()
        src0.send(b'msg')
        src1.send(b'msg')
        stream = act.zkit.EventStream(ctx)
        request.addfinalizer(stream.close)
        stream.register(dst0, stream.POLLIN)
        stream.register(dst1, stream.POLLIN)
        waiting = [dst0, dst1]
        assert stream.poll(10), 'No event ready'
        for sock, evt in stream:
            assert sock.recv() == b'msg'
            assert evt == zmq.POLLIN
            waiting.remove(sock)
            if not waiting:
                break
            assert stream.poll(10), 'No event ready'

    @pytest.fixture
    def timer(self):
        return act.zkit.SimpleTimer()

    def test_timer(self, stream, timer):
        timer.schedule(1)
        stream.register(timer, stream.TIMER)
        assert stream.poll(10), 'No event ready'
        item, event = next(stream)
        assert (item, event) == (timer, stream.TIMER)
        assert item is timer

    def test_timer_unscheduled(self, stream, timer):
        stream.register(timer, stream.TIMER)
        assert not stream.poll(5)

    def test_timer_expired_yielded(self, stream, timer):
        stream.register(timer, stream.TIMER)
        timer.schedule(1)
        assert stream.poll(10), 'No event ready'
        next(stream)
        assert not timer.active
        with pytest.raises(ValueError):
            assert timer.when
        assert not stream.poll(5)

    def test_timer_rescheduled(self, stream, timer):
        stream.register(timer, stream.TIMER)
        timer.schedule(1)
        assert stream.poll(10), 'No event ready'
        next(stream)
        timer.schedule(1)
        assert stream.poll(10), 'No event ready'
        next(stream)
        assert not stream.poll(5)

    def test_timer_two_ordered(self, stream, timer):
        timer2 = act.zkit.SimpleTimer()
        stream.register(timer, stream.TIMER)
        stream.register(timer2, stream.TIMER)
        timer.schedule(1)
        timer2.schedule(2)
        assert stream.poll(10), 'No event ready'
        assert next(stream) == (timer, stream.TIMER)
        assert stream.poll(10), 'No event ready'
        assert next(stream) == (timer2, stream.TIMER)

    def test_timer_two_identical(self, stream, timer):
        timer2 = act.zkit.SimpleTimer()
        stream.register(timer, stream.TIMER)
        stream.register(timer2, stream.TIMER)
        timer.schedule(1)
        timer2.schedule(1)
        assert stream.poll(10), 'No event ready'
        item = next(stream)[0]
        assert item is timer or item is timer2
        assert stream.poll(10), 'No event ready'
        item = next(stream)[0]
        assert item is timer or item is timer2

    def test_timer_unregistered(self, stream, timer):
        stream.register(timer, stream.TIMER)
        timer.schedule(1)
        stream.unregister(timer)
        assert not stream.poll(5)

    def test_timer_msg_ordered(self, ctx, stream, timer):
        src, dst = ctx.sockpair()
        stream.register(dst, stream.POLLIN)
        stream.register(timer, stream.TIMER)
        timer.schedule(15)
        src.send(b'msg')
        assert stream.poll(10), 'No event ready'
        assert next(stream) == (dst, stream.POLLIN)
        dst.recv()
        assert stream.poll(20), 'No event ready'
        assert next(stream) == (timer, stream.TIMER)

    def test_timer_poll_heapify(self, stream, timer):
        timer2 = act.zkit.SimpleTimer()
        timer.schedule(40)
        timer2.schedule(20)
        stream.register(timer, stream.TIMER)
        stream.register(timer2, stream.TIMER)
        timer.schedule(1)
        start = int(time.monotonic() * 1000)
        assert stream.poll(5), 'No event received'
        end = int(time.monotonic() * 1000)
        assert end - start < 15
        assert next(stream) == (timer, stream.TIMER)

    def test_timer_nosockevt(self, stream, timer):
        # Note the lack of .poll() before the next().  This makes the
        # test more likely to hang but matters because it triggers a
        # new code path.
        timer.schedule(1)
        stream.register(timer, stream.TIMER)
        assert next(stream) == (timer, stream.TIMER)

    def test_close(self, stream):
        assert not stream.closed
        stream.close()
        assert stream.closed

    def test_close_context(self):
        ctx = zmq.Context()
        stream = act.zkit.EventStream(ctx)
        stream.close()
        ctx.term()
        assert stream.closed
        assert ctx.closed

    def test_close_del(self, ctx):
        stream = act.zkit.EventStream(ctx)
        stream.__del__()
        assert stream.closed

    def test_close_noterm(self):
        ctx = zmq.Context()
        stream = act.zkit.EventStream(ctx)
        del stream
        ctx.term()

    def test_close_closed(self, stream):
        stream.close()
        assert stream.closed
        stream.close()
        for _ in stream:
            pytest.fail('No StopIteration')

    def test_term_deprecated(self, stream):
        with pytest.warns(DeprecationWarning):
            stream.term()

    def test_terminated_deprecated(self, stream):
        with pytest.warns(DeprecationWarning):
            assert not stream.terminated


class TestMessageStream:

    @pytest.fixture
    def stream(self, request, ctx):
        stream = act.zkit.MessageStream(ctx)
        request.addfinalizer(stream.close)
        return stream

    def test_single(self, ctx, stream):
        src, dst = ctx.sockpair()
        stream.register(dst)
        stream_iter = iter(stream)
        src.send(b'msg')
        msg = next(stream_iter)
        assert msg == [b'msg']
        stream.send_term()
        with pytest.raises(StopIteration):
            next(stream_iter)

    def test_multiple(self, ctx, stream):
        src0, dst0 = ctx.sockpair()
        src1, dst1 = ctx.sockpair()
        stream.register(dst0)
        stream.register(dst1)
        stream_iter = iter(stream)
        src0.send(b'msg0')
        assert next(stream_iter) == [b'msg0']
        src1.send(b'msg1')
        assert next(stream_iter) == [b'msg1']
        stream.send_term()
        with pytest.raises(StopIteration):
            next(stream_iter)

    def test_unregister(self, ctx, stream):
        src0, dst0 = ctx.sockpair()
        src1, dst1 = ctx.sockpair()
        stream.register(dst0)
        stream.register(dst1)
        src0.send(b'msg0')
        src1.send(b'msg1')
        stream_iter = iter(stream)
        for _ in range(2):
            msg = next(stream_iter)
            if msg == [b'msg1']:
                stream.unregister(dst1)
        src0.send(b'msg0')
        src1.send(b'msg1')
        assert next(stream_iter) == [b'msg0']
        stream.send_term()
        with pytest.raises(StopIteration):
            next(stream_iter)

    def test_poll_ready(self, ctx, stream):
        src, dst = ctx.sockpair()
        src.send(b'msg')
        stream.register(dst)
        assert stream.poll(3000)

    def test_poll_wait(self, ctx, stream):
        _, dst = ctx.sockpair()
        stream.register(dst)
        assert not stream.poll(10)

    def test_poll_closed(self, ctx):
        stream = act.zkit.MessageStream(ctx)
        stream.send_term()
        assert stream.poll(0) is True
        for _ in stream:
            pytest.fail('Stream not closed')

    def test_closed_attr(self, ctx):
        stream = act.zkit.MessageStream(ctx)
        assert not stream.closed
        stream.send_term()
        for _ in stream:
            pytest.fail('Stream not closed')
        assert stream.closed

    def test_next(self, ctx, stream):
        src, dst = ctx.sockpair()
        msg = [b'msg']
        src.send_multipart(msg)
        stream.register(dst)
        assert stream.poll(3000)
        assert next(stream) == msg

    def test_next_unkonwn_evt(self, ctx):
        stream = act.zkit.MessageStream(ctx)
        stream._evtstream = iter([(None, None)])
        with pytest.raises(RuntimeError):
            next(stream)

    @pytest.fixture
    def timer(self):
        return act.zkit.SimpleTimer()

    def test_timer(self, stream, timer):
        stream.register(timer)
        timer.schedule(1)
        assert stream.poll(10), 'No message ready'
        assert next(stream) == timer

    def test_timer_two_ordered(self, stream, timer):
        timer2 = act.zkit.SimpleTimer()
        stream.register(timer)
        stream.register(timer2)
        timer.schedule(1)
        timer2.schedule(2)
        assert stream.poll(10), 'No message ready'
        assert next(stream) is timer
        assert stream.poll(10), 'No message ready'
        assert next(stream) is timer2

    def test_timer_cancel(self, stream, timer):
        timer.schedule(5)
        stream.register(timer)
        assert not stream.poll(1)
        timer.cancel()
        assert not stream.poll(10)

    def test_timer_unregister(self, stream, timer):
        timer.schedule(5)
        stream.register(timer)
        assert not stream.poll(1)
        stream.unregister(timer)
        assert not stream.poll(10)

    def test_close(self, stream):
        assert not stream.closed
        stream.close()
        assert stream.closed

    def test_close_context(self):
        ctx = zmq.Context()
        stream = act.zkit.MessageStream(ctx)
        stream.close()
        ctx.term()
        assert stream.closed
        assert ctx.closed

    def test_close_del(self, ctx):
        stream = act.zkit.MessageStream(ctx)
        stream.__del__()
        assert stream.closed

    def test_close_noterm(self):
        ctx = zmq.Context()
        stream = act.zkit.MessageStream(ctx)
        del stream
        ctx.term()

    def test_term_deprecated(self, stream):
        with pytest.warns(DeprecationWarning):
            stream.term()

    def test_terminated_deprecated(self, stream):
        with pytest.warns(DeprecationWarning):
            assert not stream.terminated
