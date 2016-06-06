"""Data Object Query mapper.

pronounced `Duke` allows you to query an list, iterable or generator yielding
objects with a Django ORM like / Fluent interface.  This is useful for
exploratory programming and also it is just a nice, comfortable inteface to
query your data objects.


Example
-------
Say you had a csv file of employee records and you wanted to list the
employees in the IT department.  Well you could do the traditional thing or ...


Example::

    # bread and butter Python
    EmployeeRecord = namedtuple('EmployeeRecord', 'emp_id, name, dept, hired')

    def csvtuples():
        '''csv named tuple generator.'''
        reader = csv.reader(TEST_FILE)
        for emp in map(EmployeeRecord._make, reader):
            yield emp

    # Enter the Duke
    doq = DOQ(data_objects=csvtuples())
    for emp in doq.filter(dept='IT'):
        print(emp)

    # Now let's list everyone who is not in IT.
    for emp in doq.exclude(dept='IT'):
        print(emp)

    # ok, now let's sort the not IT employees by name
    for emp in doq.exclude(dept='IT').order_by('name'):
        print(emp)

Yes, it is just that easy. You can chain :func:`~dhp.doq.DOQ.filter` and
:func:`~dhp.doq.DOQ.exclude`. There is a :func:`~dhp.doq.DOQ.get` method that
raises :func:`~dhp.doq.DoesNotExist` and
:func:`~dhp.doq.MultipleObjectsReturned`.

All that ooohey gooey query goodness of a traditional ORM but quick and easy
and works without a lot of setup.

One quick note before we head into the full documenation. DOQ is NOT a full
blown Object Relation Manager. It does not create databases, nor know how to
access them. If that is what you desire, then SQLAlchemy, Pony, PeeWeeDB or
Django's ORM is probably going to get you what you want.

If you are looking to slap some lipstick on a simple data source, well then,
DOQ is just your color.
"""

import operator
import random

OPERATORS = {
    'exact': operator.eq,
    'iexact': lambda a, b: a.lower() == b.lower(),
    'lt': operator.lt,
    'lte': operator.le,
    'gt': operator.gt,
    'gte': operator.ge,
    'contains': operator.contains,
    'icontains': lambda a, b: b.lower() in a.lower(),
    'startswith': lambda a, b: a.startswith(b),
    'istartswith': lambda a, b: a.lower().startswith(b.lower()),
    'endswith': lambda a, b: a.endswith(b),
    'iendswith': lambda a, b: a.lower().endswith(b.lower()),
    'in': lambda a, b: a in b,
    'range': lambda a, b: (a >= b[0]) & (a <= b[1])
}


class DoesNotExist(Exception):
    """Raised when no object is found."""
    pass


class MultipleObjectsReturned(Exception):
    """raised when more than 1 object returned but should not be."""
    pass

MAX_REPR_ITEMS = 3


# pylint: disable=W0212
# Light Weight Data Object Query Mapper
class DOQ(object):
    """data object query mapper."""
    def __init__(self, data_objects):
        self._data_objects = data_objects
        self._ops = []
        self._order_by = []
        self._result_cache = None

    def __getitem__(self, k):
        self._fetch_all()
        return self._result_cache[k]

    def __iter__(self):
        self._fetch_all()
        for obj in self._result_cache:
            yield obj

    def __len__(self):
        return self.count

    def __repr__(self):
        self._fetch_all()
        response = ','.join([str(x) for x in self[0:MAX_REPR_ITEMS]])
        if len(self._result_cache) > MAX_REPR_ITEMS:
            response += '...(remaining elements truncated)...'
        return response

    def _fetch_all(self):
        '''Run the query and fill _result_cache.'''
        if self._result_cache is None:
            self._result_cache = list(self._execute())

    def _clone(self):
        '''Clone and return the object with the new parameters.

        a/k/a Fluent Interface'''
        clone = self.__class__(self._data_objects)
        clone._ops = self._ops[:]
        clone._order_by = self._order_by[:]
        return clone

    def _gather(self, negate, **look_ups):
        """gather any attribute name lookups."""
        for key in look_ups:
            num = len(key.split('__'))
            if num == 1:
                attr_names = [key, ]
                operand = 'exact'
            else:
                if key.split('__')[-1] in OPERATORS:
                    operand = key.split('__')[-1]
                    attr_names = key.split('__')[:-1]
                else:
                    operand = 'exact'
                    attr_names = key.split('__')
            val = look_ups[key]
            self._ops.append((negate, attr_names, OPERATORS[operand], val))

    def _execute(self):
        """execute the filter and return an iterable."""
        data = self._data_objects
        if self.ordered:
            if not isinstance(data, list):
                data = list(data)
            for reverse, attr_name in self._order_by:
                if attr_name == '?':
                    random.shuffle(data)
                else:
                    key_fn = self.order_by_key_fn(attr_name)
                    data.sort(key=key_fn, reverse=reverse)

        for plst in data:
            match = True
            for negate, attr_names, operand, val in self._ops:
                thing = plst
                for attr_name in attr_names:
                    thing = getattr(thing, attr_name)
                if negate:
                    if operand(thing, val):
                        match = False
                        break
                else:
                    if not operand(thing, val):
                        match = False
                        break
            if match:
                yield plst

    def all(self):
        '''Returns a cloned DOQ.  Short hand for an empty filter but it reads
        more naturally than ``doq.filter()``.

        Args:
            None

        Returns:
            DOQ: A cloned DOQ object.

        Example::

            for obj in doq.all():
                print(obj)

        '''
        clone = self._clone()
        return clone

    @property
    def count(self):
        """A property that returns the number of objects currently selected.
        Can also use len(doq).

        Returns:
            (int): The number of objects selected.


        Example::

            if doq.filter(name='Jeff').count == 1:
                do_something
            result = doq.filter(emp_id=1)
            assert doq.count == len(doq)
        """
        self._fetch_all()
        return len(self._result_cache)

    def filter(self, **look_ups):
        """Returns a new DOQ containing objects that match the given lookup
        parameters.

        Args:
            look_ups: The lookup parameters should be in the format
                described in `Attribute Lookups`_ below. Multiple parameters
                are joined via AND in the underlying logic.

        Returns:
            DOQ: A cloned DOQ object with the specified filter(s).

        Raises:
            AttributeError: If an attribute_name in the look_ups specified can
                not be found.

        Example::

            doq.filter(name='Foo', hired__gte='2012-01-03')
        """
        clone = self._clone()
        clone._gather(False, **look_ups)
        return clone

    def get(self, **look_ups):
        """Preform a get operation using 0 or more filter keyword arguments.
        A single object should be returned.

        Args:
            look_ups: The lookup parameters should be in the format
                described in `Attribute Lookups`_ below. Multiple parameters
                are joined via AND in the underlying logic.

        Returns:
            data_object: A single matching data_object from data_objects.

        Raises:
            AttributeError: If an attribute_name in the look_ups specified can
                not be found.

        Example::

            obj = doq.get(emp_id=1)

        Raises:
            DoesNotExist: If no matching object is found.
            MultipleObjectsReturned: If more than 1 object is found.
        """
        clone = self._clone()
        clone._gather(False, **look_ups)
        result = list(clone)
        num = len(result)
        if num == 1:
            return result[0]
        if not num:
            raise DoesNotExist(
                "%s matching query does not exist." % self.__class__.__name__)
        msg = "get() returned more than one %s -- it returned %s!"
        raise MultipleObjectsReturned(msg % (self.__class__.__name__, num))

    @staticmethod
    def get_attr(obj, attrname):
        '''Retrieve a possibly nested attribute value.

        Args:
            obj(data object): The data object to retrieve the value.
            attrname(str): The attribute name/path to retrieve. A simple
                object access might be `name`, a nested object value might be
                `address__city`

        Returns:
            The value of the indicated attribute.

        '''
        for attr_name in attrname.split('__'):
            obj = getattr(obj, attr_name)
        return obj

    def exclude(self, **look_ups):
        """Returns a new DOQ containing objects that **do not match** the
        given lookup parameters.

        Args:
            look_ups: The lookup parameters should be in the format
                described in `Attribute Lookups`_ below. Multiple parameters
                are joined via AND in the underlying logic, and the whole
                thing is enclosed in a NOT.

        Returns:
            DOQ: A cloned DOQ object with the specified exclude(s).

        Raises:
            AttributeError: If an attribute_name in the look_ups specified can
                not be found.

        This example excludes all entries whose hired date is later than
        2005-1-3 AND whose name is "Jeff"::

            doq.exclude(hired__gt=datetime.date(2005, 1, 3), name='Jeff')
        """
        clone = self._clone()
        clone._gather(True, **look_ups)
        return clone

    def order_by(self, *attribute_names):
        '''Return a new DOQ with thes results ordered by the data_object's
        attribute(s).  The default order is assending. Use a minus (-) sign in
        front of the attribute name to indicate descending order. Repeated
        .order_by calls are NOT additive, they replace any existing ordering.

        Args:
            attribute_names: 0 or more data_object attribute names. Listed
                from most significant order to least.

        Returns:
            DOQ: A new DOQ object with the specified ordering.

        Example::

            doq.all().order_by('emp_id')  # emp_id 1, 2, 3, ..., n
            doq.all().order_by('-emp_id') # emp_id n, n-1, n-2, ..., 1

            doq.all().order_by('dept', 'emp_id') # by dept, then by emp_id

        to order randomly, use a '?'. ::

            doq.all().order_by('?')
        '''
        clone = self._clone()
        attr_names = list(attribute_names)
        clone._order_by = []     # replace current ordering
        while attr_names:
            order = attr_names.pop()
            reverse = False
            if order.startswith('-'):
                reverse = True
                order = order[1:]
            clone._order_by.append((reverse, order))
        return clone

    @staticmethod
    def order_by_key_fn(attrname):
        '''Override this method to supply a new key function for the order_by
        method.

        The default function is::

            lambda obj: DOQ.get_attr(obj, attrname)

        If you had an attribute "emp_id" that returned a number as a string
        ``['2', '1', '3', '11']``. It would be ordered by string conventions
        returning them in ``['1', '11', '2', '3']``. If you want them sorted
        like integers ``['1', '2', '3', '11']``, you would subclass DOQ and
        override the ```order_by_key_fn`` like this::

            class MyDOQ(DOQ):
                @staticmethod
                def order_by_key_fn(attrname):
                    if attrname == 'emp_id':
                        def key_fn(obj):
                            # return attr as an integer
                            return int(DOQ.get_attr(obj, attrname))
                    else:
                        def key_fn(obj):
                            # return the standard function.
                            return DOQ.get_attr(obj, attrname)
                    return key_fn

            mydoq = MyDOQ(data_objects)
            mydoq.all().order_by('emp_id')

        Args:
            attrname (str): The attribute name be acted on by the order_by
                method.
        Returns:
            function: A function that takes the attribute name as an argument
                and that also has access to the object be acted on.

        Raises:
            AttributeError: If the attribute_name specified can not be found.
        '''
        return lambda obj: DOQ.get_attr(obj, attrname)

    @property
    def ordered(self):
        '''True if an order is set, otherwise False.

        Returns:
            bool: True if the order_by is set, otherwise False.

        Example::

            results = doq.all()
            assert results.ordered == False
            results = results.order_by('name')
            assert results.ordered == True

        '''
        return len(self._order_by) > 0
