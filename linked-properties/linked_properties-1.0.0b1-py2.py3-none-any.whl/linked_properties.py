# coding=utf-8

"""
linked_properties provides the classes 'WatchableProperty', 'WatchableInstance' and 'LinkableProperty', and the function
'unbind'.
While WatchableInstance may be rarely used, it is provided for the user of this micro-library to be able to create
deriviative classes to LinkableProperty and annotate them properly.

More informations to the classes and the function my be found in their or its docstrings.

But be aware that all "property" objects here _do not_ subclass property, and work a little differently.
Using @x.getter actually *sets* the getter instead of returning a changed property object.

made by CodenameLambda
"""

from typing import Optional, Callable, List, Tuple, Dict
from weakref import ref, ReferenceType


class _ReferenceWithId(object):
    """
    holds a weak reference and the id of an object
    """

    def __init__(self, s: object) -> None:
        self.ref = ref(s)  # type: ReferenceType
        self.id = id(s)  # type: int


class _Property(object):
    """
    a slight variation of the builtin property, it is mutable and changes at .getter(), .setter() and .deleter() instead
    of returning a new object.
    """

    def __init__(self, fget: Optional[Callable[[object], object]] = None,
                 fset: Optional[Callable[[object, object], None]] = None,
                 fdel: Optional[Callable[[object], None]] = None,
                 doc: str = None):
        self.fget = fget  # type: Optional[Callable[[object], object]]
        self.fset = fset  # type: Optional[Callable[[object, object], None]]
        self.fdel = fdel  # type: Optional[Callable[[object], None]]
        if doc is None and fget is not None:
            doc = fget.__doc__
        self.__doc__ = doc  # type: Optional[str]

    def __get__(self, obj: object, owner: Optional[object] = None) -> object:
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        return self.fget(obj)

    def __set__(self, obj: object, value: object) -> None:
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(obj, value)

    def __delete__(self, obj: object) -> None:
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(obj)

    def getter(self, fget: Callable[[object], object]) -> '_Property':
        """
        Set the getter for the _Property to fget.
        """
        self.fget = fget
        return self

    def setter(self, fset: Callable[[object, object], None]) -> '_Property':
        """
        Set the setter for the _Property to fset.
        """
        self.fset = fset
        return self

    def deleter(self, fdel: Callable[[object], None]) -> '_Property':
        """
        Set the deleter for the _Property to fdel.
        """
        self.fdel = fdel
        return self


class WatchableProperty(_Property):
    """
    WatchableProperty is a class that is used to create a property that can be submitted to a LinkableProperty.

    It works exactly the same as "property", except for the name.

    If a linked property is reading from another one, than this object may be blocked for writing for the instance in
    question.
    To get around this, you may define an "at_blocked_set" function, that unlocks the linked property by setting it to
    None. It may return true or false, if it is true, the __set__ function is called another time.

    Note: the at_blocked_set function can reinvoke the __set__ function only once per tried write access!
    """

    def __init__(self, getter: Optional[Callable[[], object]] = None,
                 setter: Optional[Callable[[object], None]] = None) -> None:
        super().__init__(getter, setter)

        self.notified = []  # type: List[Callable[[object, object], None]]
        self.blocked_instance_ids = []  # type: List[int]

        self.f_at_blocked_set = None  # type: Optional[Callable[[object, object], None]]

    def get_notified(self, f: Callable[[], None]) -> None:
        """
        Give notifications to f, if the value changed. Cannot be revoked.
        """
        self.notified.append(f)

    def __set__(self, s: object, value: object, second_try: bool = False) -> None:
        if id(s) in self.blocked_instance_ids:
            if not second_try and self.f_at_blocked_set is not None and self.f_at_blocked_set(s, value):
                self.__set__(s, value, True)
            else:
                raise BlockingIOError(
                    "This property is blocked_instance_ids for writing by a reading LinkableProperty.")
        for i in self.notified:
            i(s, value)
        if self.fset is not None:
            self.fset(s, value)
        else:
            raise AttributeError("can't delete attribute")

    def block(self, i: int) -> None:
        """
        Block the setter for the object with the id "i". Can be revoked by release()
        """
        self.blocked_instance_ids.append(i)

    def release(self, i: int) -> None:
        """
        Revoke block() for i
        """
        if i in self.blocked_instance_ids:
            self.blocked_instance_ids.remove(i)

    def at_blocked_set(self, f: Callable[[object, object], bool]) -> 'WatchableProperty':
        """
        Create an at_blocked_set function. It may return a boolean and will be invoked by its object and the value that
        was tried to be assigned.
        """
        self.f_at_blocked_set = f
        return self

    def __delete__(self, instance: object) -> None:
        raise AttributeError("can't delete attribute")

    def deleter(self, fdel: Callable[[object], None]) -> 'WatchableProperty':
        """
        This raises an AttributeError, because you cannot define a deleter for a WatchableProperty.
        This is true because you can't even delete a watchable attribute.
        """
        raise AttributeError("A associated_watchable property can't be deleted.")


class LinkingTransmission(object):
    """
    LinkingTransmission is an object used to transmit links and connect the two parties together.
    """

    def __init__(self, initial_value: object, formula: Optional[Callable[[object], object]] = None) -> None:
        self.watching_functions = []  # type: List[Tuple[int, Callable[[object, object], None]]]
        self.current_value = formula(initial_value)  # type: object
        self.is_destroyed = False  # type: bool
        self.formula = lambda x: x if formula is None else formula  # type: Callable[[object], object]

    def update(self, new_value: object) -> None:
        """
        Notify all watching functions about the changed current_value
        """
        self.current_value = self.formula(new_value)

        for id_, watching_function in self.watching_functions:
            watching_function(id_, new_value)

    def watch(self, watcher: Callable[[object, object], None], id_: int) -> None:
        """
        Create a new watching_functions function, s is the first argument that'll get passed to the function.
        """
        self.watching_functions.append((id_, watcher))

    def stop_watching(self, id_: int) -> None:
        """
        Stop watching_functions for id_
        """
        for i, v in enumerate(self.watching_functions):
            if v[0] == id_:
                del self.watching_functions[i]
                return

    def destroy(self) -> None:
        """
        Mark the parent attribute as is_destroyed
        """
        self.is_destroyed = True


class LinkableProperty(_Property):
    """
    The main functionality: The LinkableProperty allows you to do this:

    0001| import linked_properties
    0002|
    0003|
    0004| class A(linked_properties.Object):
    0005|     def __init__(self) -> None:
    0006|         self._x = 0  # type: int
    0007|
    0008|     def _getx(self) -> int:
    0009|         return self._x
    0010|
    0011|     def _setx(self, current_value: int) -> None:
    0012|         self._x = current_value
    0013|
    0014|     x = linked_properties.WatchableProperty(_getx, _setx)  # type: linked_properties.WatchableProperty
    0015|     # you could use function decorators as well, but this annoyes the PyCharm type checking system...
    0016|
    0017|     l_x = linked_properties.LinkableProperty(x)  # type: linked_properties.LinkableProperty
    0018|
    0019| a1 = A()
    0020| a2 = A()
    0021| a1.x = 1
    0022| a1.l_x = a2.l_x
    0023| print(a1.x, "; expected 0")
    0024| a2.x = 3
    0025| print(a1.x, "; expected ")
    0026| a1.l_x = None
    0027| print(a1.x, "; expected 3")
    0028| a1.x = 2
    0029| print(a1.x, "; expected 2")
    0030| print(a2.x, "; expected 3")
    0031| a1.l_x = a2.l_x
    0032| a1.x = 3  # should yield a BlockingIOError

    This will print 3, because the change of x in a2 triggered the change in a1.
    Note: a1.x is blocked_instance_ids for writing as long as a linked property is linked to it's current_value.
    """

    def __init__(self, watchable: WatchableProperty) -> None:
        super().__init__()

        self.associated_watchable = watchable  # type: WatchableProperty
        self.associated_watchable.get_notified(self._notify)

        self.own_transmissions_per_instance = {}  # type: Dict[int, List[LinkingTransmission]]
        self.transmission_per_instance = {}  # type: Dict[int, LinkingTransmission]

        self.weak_references_with_ids = []  # type: List[_ReferenceWithId]

    def _cleanup(self) -> None:
        already_deleted = 0

        for i in self.transmission_per_instance:
            if self.transmission_per_instance[i].is_destroyed:
                del self.transmission_per_instance[i]
                self.associated_watchable.release(i)

        for i, v in enumerate(self.weak_references_with_ids):
            if v.ref() is None:
                if v.id in self.own_transmissions_per_instance:
                    del self.own_transmissions_per_instance[v.id]
                if v.id in self.transmission_per_instance:
                    self.transmission_per_instance[v.id].stop_watching(v.id)
                    del self.transmission_per_instance[v.id]
                del self.weak_references_with_ids[i - already_deleted]
                already_deleted += 1

    def get_new_transmission(self, s: object, owner: Optional[object] = None,
                             formula: Optional[Callable[[object], object]] = None) -> LinkingTransmission:
        """
        Create a new transmission with formula.
        """
        if s is None:
            return self

        self._cleanup()

        out = LinkingTransmission(self.associated_watchable.fget(s), formula)
        if id(s) not in self.own_transmissions_per_instance:
            self.own_transmissions_per_instance[id(s)] = [out]
            if id(s) not in self.transmission_per_instance:
                self.weak_references_with_ids.append(_ReferenceWithId(s))
        else:
            self.own_transmissions_per_instance[id(s)].append(out)

        return out

    def __get__(self, s: object, owner: Optional[object] = None,
                formula: Optional[Callable[[object], object]] = None) -> LinkingTransmission:
        return self.get_new_transmission(s, owner, formula)

    def __set__(self, s: object, value: Optional[LinkingTransmission]) -> None:
        self._cleanup()

        if value is not None:
            value.watch(self._watch, id(s))
            self.transmission_per_instance[id(s)] = value  # overwritten if needed
            if id(s) not in self.own_transmissions_per_instance:
                self.own_transmissions_per_instance[id(s)] = []
                if id(s) not in self.weak_references_with_ids:
                    self.weak_references_with_ids.append(_ReferenceWithId(s))
            self.associated_watchable.block(id(s))

            # copy current_value:
            self.associated_watchable.__set__(s, value.current_value)
        else:
            del self.transmission_per_instance[id(s)]
            self.associated_watchable.release(id(s))

    def _notify(self, s: object, value: object) -> None:
        self._cleanup()

        if id(s) not in self.own_transmissions_per_instance:
            return
        for i in self.own_transmissions_per_instance[id(s)]:
            i.update(value)

    def _watch(self, id_: int, value: object, transmission: LinkingTransmission) -> None:
        self._cleanup()

        s = None
        found = False
        for i in self.weak_references_with_ids:
            if i.id == id_:
                s = i.ref()
                found = True
                break

        if not found:
            transmission.stop_watching(id_)
            return

        self.associated_watchable.fset(s, value)
        for i in self.own_transmissions_per_instance[id(s)]:
            i.update(value)

    def __delete__(self, instance) -> None:
        raise AttributeError("can't delete attribute")

    def getter(self, fget: Callable[[object], object]) -> 'LinkableProperty':
        """
        This raises an AttributeError, because you cannot define a getter for a LinkedPropety.
        """
        raise AttributeError("You cannot define a getter for a LinkableProperty")

    def setter(self, fset: Callable[[object, object], None]) -> 'LinkableProperty':
        """
        This raises an AttributeError, because you cannot define a setter for a LinkedPropety.
        """
        raise AttributeError("You cannot define a setter for a LinkableProperty")

    def deleter(self, fdel: Callable[[object], None]) -> 'LinkableProperty':
        """
        This raises an AttributeError, because you cannot define a deleter for a LinkedPropety.
        This is true because you can't even delete a linkable attribute.
        """
        raise AttributeError("A linkable property can't be deleted")
