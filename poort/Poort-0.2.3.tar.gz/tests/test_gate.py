# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from poort import Gate
from pytest import raises
from threading import Thread
from time import sleep


class TestGate(object):
    def test_basics(self):
        gate = Gate()
        gate.setup(dict())

        gate.attach('text', 'Hallo world!')
        assert gate.retrieve('text') == 'Hallo world!'
        assert gate.contains('text')
        gate.release('text')
        assert not gate.contains('text')

        gate.teardown()

        with raises(RuntimeError):
            gate.teardown()

    def test_threaded(self):
        gate = Gate()

        def wrap(nr, sleep_time):
            with gate(dict()):
                gate.attach('counter', nr)

                sleep(sleep_time)

                assert gate.contains('counter')
                assert gate.retrieve('counter') == nr

                assert len(gate.local.gate_registered_names)

        thread_1 = Thread(target=wrap, args=(1, 0.2,))
        thread_2 = Thread(target=wrap, args=(2, 0.1,))

        thread_1.start()
        thread_2.start()

        thread_1.join()
        thread_2.join()

        assert not hasattr(gate.local, 'gate_registered_names')

    def test_exceptions(self):
        gate = Gate()
        gate.setup(dict())

        with raises(RuntimeError):
            gate.setup(dict())

        with raises(ValueError):
            gate.retrieve('does-not-exist')

        gate.teardown()

        with raises(RuntimeError):
            gate.teardown()
