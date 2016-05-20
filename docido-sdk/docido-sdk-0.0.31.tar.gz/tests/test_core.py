import unittest

from docido_sdk.core import (
    Component,
    ExtensionPoint,
    implements,
    Interface,
)
from docido_sdk.core import DocidoError
from docido_sdk.env import Environment


class Foobar(Interface):
    pass


class FooInterface(Interface):
    def foo():
        pass


class FooComponent(Component):
    implements(FooInterface, Foobar)


class BarInterface(Interface):
    pass


class BarComponent(Component):
    implements(BarInterface, Foobar)


class Pika(Interface):
    pass


class TestCore(unittest.TestCase):
    def test_expect_1_when_0(self):
        class expect_one_pika(Component):
            pika = ExtensionPoint(Pika, unique=True)
        env = Environment()
        consumer = env[expect_one_pika]
        with self.assertRaises(Exception) as exc:
            consumer.pika
        self.assertEqual(
            exc.exception.message,
            "Expected one 'Pika' component, but found 0"
        )

    def test_extensionpoint_repr(self):
        foos = ExtensionPoint(FooInterface)
        self.assertEqual(foos.__repr__(), '<ExtensionPoint FooInterface>')

    def test_abstract_component_not_registered(self):
        from docido_sdk.core import ComponentMeta

        class AbstractComponent(Component):
            abstract = True

        class ConcreteComponent(Component):
            pass
        self.assertNotIn(AbstractComponent, ComponentMeta._components)
        env = Environment()
        env[ConcreteComponent]
        with self.assertRaises(DocidoError):
            env[AbstractComponent]
        self.assertFalse(AbstractComponent in env)
        self.assertTrue(ConcreteComponent in env)
        self.assertTrue(env.is_component_enabled(ConcreteComponent))
        self.assertTrue(env.is_component_enabled(AbstractComponent))

    def test_expect_1_when_more(self):
        class expect_one_foobar(Component):
            foobar = ExtensionPoint(Foobar, unique=True)
        env = Environment()
        consumer = env[expect_one_foobar]
        with self.assertRaises(Exception) as exc:
            consumer.foobar
        self.assertEqual(
            exc.exception.message,
            "Expected one 'Foobar' component, but found 2: "
            "BarComponent, FooComponent"
        )

    def test_disable_component(self):
        class MyEnv(Environment):
            def is_component_enabled(self, component):
                print 'component activated %r' % component
                if 'foo' in component.__name__.lower():
                    print '> returning False'
                    return False
                return True

        class FilteredFooComponent(Component):
            pass

        class UnFilteredBarComponent(Component):
            pass
        env = MyEnv()
        self.assertIsNone(env[FilteredFooComponent])
        unfiltered_component = env[UnFilteredBarComponent]
        self.assertIsNotNone(unfiltered_component)
        env.disable_component(UnFilteredBarComponent)
        self.assertIsNone(env[UnFilteredBarComponent])

        env.disable_component(unfiltered_component)
        self.assertIsNone(env[UnFilteredBarComponent])

    def test_component_with_invalid_constructor(self):
        class SpuriousComponent(Component):
            def __init__(self, env, another_parameter):
                pass
        env = Environment()
        with self.assertRaises(DocidoError) as exc:
            env[SpuriousComponent]
        error_message = 'Unable to instantiate component <class'
        self.assertTrue(exc.exception.message.startswith(error_message))


if __name__ == '__main__':
    unittest.main()
