
class TestLocalComponents:
    _components = []

    @classmethod
    def add(cls, component):
        cls._components.append(component)
        return component

    @classmethod
    def cleanup(cls):
        for component in cls._components:
            component.unregister()

cleanup_component = TestLocalComponents.add
cleanup_components = TestLocalComponents.cleanup
