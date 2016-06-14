from mock import Mock
from unittest import TestCase
from preggy import expect

from exec_pypeline import Pipeline
from .pass_action import PassAction


class FirstAction(PassAction):
    name = "My first action"


class SecondAction(PassAction):
    name = "My second action"


class ThirdAction(PassAction):
    name = "My third action"


class BoomAction(PassAction):
    name = "My boom action"

    def forward(self, context):
        raise RuntimeError("Boom")


class PipelineTestCase(TestCase):

    def test_my_pipe(self):
        first = FirstAction()
        second = SecondAction()
        third = ThirdAction()
        first.forward = Mock()
        second.forward = Mock()
        third.forward = Mock()
        first.backward = Mock()
        second.backward = Mock()
        third.backward = Mock()
        action_list = [first, second, third]
        pipe = Pipeline(action_list)
        expect(pipe.action_list).to_equal(action_list)
        expect(pipe.execute()).Not.to_be_an_error()
        expect(first.forward.call_count).to_equal(1)
        expect(second.forward.call_count).to_equal(1)
        expect(third.forward.call_count).to_equal(1)
        expect(first.backward.call_count).to_equal(0)
        expect(second.backward.call_count).to_equal(0)
        expect(third.backward.call_count).to_equal(0)

    def test_my_boom_pipe(self):
        first = FirstAction()
        second = SecondAction()
        boom = BoomAction()
        third = ThirdAction()
        first.forward = Mock()
        second.forward = Mock()
        third.forward = Mock()
        first.backward = Mock()
        second.backward = Mock()
        boom.backward = Mock()
        third.backward = Mock()
        action_list = [first, second, boom, third]
        pipe = Pipeline(action_list)
        expect(pipe.action_list).to_equal(action_list)
        expect(pipe.execute()).Not.to_be_an_error()

        expect(first.forward.call_count).to_equal(1)
        expect(second.forward.call_count).to_equal(1)
        expect(third.forward.call_count).to_equal(0)

        expect(first.backward.call_count).to_equal(1)
        expect(second.backward.call_count).to_equal(1)
        expect(boom.backward.call_count).to_equal(1)
        expect(third.backward.call_count).to_equal(0)

    def test_execute_with_empty_context(self):
        first = FirstAction()
        second = SecondAction()
        pipe = Pipeline([first, second])
        expect(pipe.execute({})).to_equal(pipe.actions_to_dict())

    def test_get_titles(self):
        first = FirstAction()
        second = SecondAction()
        pipe = Pipeline([first, second])
        expect(pipe.get_titles()).to_equal([first.name, second.name])

    def test_get_statuses(self):
        first = FirstAction()
        second = SecondAction()
        pipe = Pipeline([first, second])
        expect(pipe.get_statuses()).to_equal([first.status, second.status])

    def test_actions_to_dict(self):
        first = FirstAction()
        second = SecondAction()
        pipe = Pipeline([first, second])
        expect(pipe.actions_to_dict()).to_equal([{
            'id': first.id,
            'name': first.name,
            'status': first.status,
            'error': {
                'msg': None,
                'traceback': None,
                'class': None,
            },
            'outcome': None,
        }, {
            'id': second.id,
            'name': second.name,
            'status': second.status,
            'error': {
                'msg': None,
                'traceback': None,
                'class': None,
            },
            'outcome': None,
        }])

    def test_from_dict_method(self):
        first = FirstAction()
        second = SecondAction()
        pipe = Pipeline([first, second])
        pipe2 = Pipeline.from_dict(pipe.actions_to_dict())
        expect(pipe.actions_to_dict()).to_equal(pipe2.actions_to_dict())


class PipelineActionListInClassTestCase(TestCase):
    def test_pipeline(self):
        first = FirstAction()
        second = SecondAction()

        class TestPipe(Pipeline):
            action_list = [first, second]

        expect(TestPipe().execute()).to_equal([first.to_dict(), second.to_dict()])


class PipelineIterTestCase(TestCase):
    def test_my_pipe(self):
        first = FirstAction()
        second = SecondAction()
        third = ThirdAction()
        first.forward = Mock()
        second.forward = Mock()
        third.forward = Mock()
        first.backward = Mock()
        second.backward = Mock()
        third.backward = Mock()
        action_list = [first, second, third]
        pipe = Pipeline(action_list)
        expect(pipe.action_list).to_equal(action_list)

        gen = pipe.iter_execute()
        expect(gen).Not.to_be_an_error()

        expect(first.forward.call_count).to_equal(0)
        expect(second.forward.call_count).to_equal(0)
        expect(third.forward.call_count).to_equal(0)
        expect(first.backward.call_count).to_equal(0)
        expect(second.backward.call_count).to_equal(0)
        expect(third.backward.call_count).to_equal(0)

        for i, a in enumerate(gen):
            index = i + 1
            expect(first.forward.call_count).to_equal(int(bool(index / 1)))
            expect(second.forward.call_count).to_equal(int(bool(index / 2)))
            expect(third.forward.call_count).to_equal(int(bool(index / 3)))
            expect(first.backward.call_count).to_equal(0)
            expect(second.backward.call_count).to_equal(0)
            expect(third.backward.call_count).to_equal(0)

    def test_my_boom_pipe(self):
        first = FirstAction()
        second = SecondAction()
        boom = BoomAction()
        third = ThirdAction()
        first.forward = Mock()
        second.forward = Mock()
        third.forward = Mock()
        first.backward = Mock()
        second.backward = Mock()
        boom.backward = Mock()
        third.backward = Mock()
        action_list = [first, second, boom, third]
        pipe = Pipeline(action_list)
        expect(pipe.action_list).to_equal(action_list)
        gen = pipe.iter_execute()
        expect(gen).Not.to_be_an_error()

        expect(first.forward.call_count).to_equal(0)
        expect(second.forward.call_count).to_equal(0)
        expect(third.forward.call_count).to_equal(0)
        expect(first.backward.call_count).to_equal(0)
        expect(second.backward.call_count).to_equal(0)
        expect(third.backward.call_count).to_equal(0)

        for i, a in enumerate(gen):
            index = i + 1
            expect(first.forward.call_count).to_equal(int(bool(index / 1)))
            expect(second.forward.call_count).to_equal(int(bool(index / 2)))
            expect(third.forward.call_count).to_equal(0)
            expect(boom.backward.call_count).to_equal(int(bool(index / 3)))
            expect(second.backward.call_count).to_equal(int(bool(index / 4)))
            expect(first.backward.call_count).to_equal(int(bool(index / 5)))
            expect(third.backward.call_count).to_equal(0)

    def test_execute_with_empty_context(self):
        first = FirstAction()
        second = SecondAction()
        pipe = Pipeline([first, second])
        result = []
        for a in pipe.iter_execute({}):
            result.append(a)
        expect(result).to_equal(pipe.action_list)
