# -*- coding: utf-8 -*-
from app import cached_type
import model


def create(parent):
    """Create the classes inside this parent"""
    kwargs = {}
    kwargs['prefix'] = ''
    kwargs['parent'] = parent
    kwargs['readonly'] = True

    #containers folder
    kwargs['name'] = 'containers'
    folder = model.Folder(**kwargs)

    #array folder
    kwargs['parent'] = folder
    kwargs['name'] = 'array'
    array_folder = model.Folder(**kwargs)

    #std::array
    kwargs['parent'] = array_folder
    kwargs['name'] = 'array'
    kwargs['is_struct'] = True
    kwargs['template'] = 'class T, std::size_t N'
    kwargs['template_types'] = ['T']
    cls = model.cc.Class(**kwargs)

    kwargs['parent'] = cls
    kwargs['template'] = None
    kwargs['name'] = 'types'
    folder_types = model.Folder(**kwargs)

    kwargs['parent'] = folder_types
    kwargs['name'] = 'value_type'
    kwargs['definition'] = 'typedef T value_type;'
    value_type = model.cc.Type(**kwargs)

    kwargs['name'] = 'size_type'
    kwargs['definition'] = 'typedef std::size_t size_type;'
    size_type = model.cc.Type(**kwargs)

    kwargs['name'] = 'difference_type'
    kwargs['definition'] = 'typedef std::ptrdiff_t difference_type;'
    difference_type = model.cc.Type(**kwargs)

    kwargs['name'] = 'reference'
    kwargs['definition'] = 'typedef value_type& reference;'
    reference = model.cc.Type(**kwargs)

    kwargs['name'] = 'const_reference'
    kwargs['definition'] = 'typedef const value_type& const_reference;'
    const_reference = model.cc.Type(**kwargs)

    kwargs['name'] = 'pointer'
    kwargs['definition'] = 'typedef value_type* pointer;'
    pointer = model.cc.Type(**kwargs)

    kwargs['name'] = 'const_pointer'
    kwargs['definition'] = 'typedef const value_type* const_pointer;'
    const_pointer = model.cc.Type(**kwargs)

    kwargs['name'] = 'iterator'
    kwargs['definition'] = 'typedef RandomAmodelessIterator iterator;'
    iterator = model.cc.Type(**kwargs)

    kwargs['name'] = 'const_iterator'
    kwargs['definition'] = 'typedef Constant random access iterator const_iterator;'
    const_iterator = model.cc.Type(**kwargs)

    kwargs['name'] = 'reverse_iterator'
    kwargs['definition'] = 'typedef std::reverse_iterator<iterator> reverse_iterator;'
    reverse_iterator = model.cc.Type(**kwargs)

    kwargs['name'] = 'const_reverse_iterator'
    kwargs['definition'] = 'typedef std::reverse_iterator<const_iterator> const_reverse_iterator;'
    const_reverse_iterator = model.cc.Type(**kwargs)

    ## member functions
    kwargs['parent'] = cls
    kwargs['name'] = 'member functions'
    folder_methods = model.Folder(**kwargs)

    ## ## element access
    kwargs['parent'] = folder_methods
    kwargs['name'] = 'element access'
    folder_element_access = model.Folder(**kwargs)

    kwargs['parent'] = folder_element_access
    kwargs['name'] = 'at'
    kwargs['type'] = model.cc.typeinst(type=reference)
    at0 = model.cc.MemberMethod(**kwargs)

    kwargs['parent'] = at0
    kwargs['name'] = 'pos'
    kwargs['type'] = model.cc.typeinst(type=size_type)
    model.cc.Argument(**kwargs)

    kwargs['parent'] = folder_element_access
    kwargs['name'] = 'at'
    kwargs['type'] = model.cc.typeinst(type=const_reference)
    kwargs['constmethod'] = True
    at1 = model.cc.MemberMethod(**kwargs)

    kwargs['parent'] = at1
    kwargs['name'] = 'pos'
    kwargs['type'] = model.cc.typeinst(type=size_type)
    model.cc.Argument(**kwargs)

    kwargs['parent'] = folder_element_access
    kwargs['name'] = 'operator []'
    kwargs['type'] = model.cc.typeinst(type=reference)
    kwargs['constmethod'] = False
    aop0 = model.cc.MemberMethod(**kwargs)

    kwargs['parent'] = aop0
    kwargs['name'] = 'pos'
    kwargs['type'] = model.cc.typeinst(type=size_type)
    model.cc.Argument(**kwargs)

    kwargs['parent'] = folder_element_access
    kwargs['name'] = 'operator []'
    kwargs['type'] = model.cc.typeinst(type=const_reference)
    kwargs['constmethod'] = True
    aop1 = model.cc.MemberMethod(**kwargs)

    kwargs['parent'] = aop1
    kwargs['name'] = 'pos'
    kwargs['type'] = model.cc.typeinst(type=size_type)
    model.cc.Argument(**kwargs)

    kwargs['parent'] = folder_element_access
    kwargs['name'] = 'front'
    kwargs['type'] = model.cc.typeinst(type=reference)
    kwargs['constmethod'] = False
    model.cc.MemberMethod(**kwargs)

    kwargs['parent'] = folder_element_access
    kwargs['name'] = 'front'
    kwargs['type'] = model.cc.typeinst(type=const_reference)
    kwargs['constmethod'] = True
    model.cc.MemberMethod(**kwargs)

    kwargs['parent'] = folder_element_access
    kwargs['name'] = 'back'
    kwargs['type'] = model.cc.typeinst(type=reference)
    kwargs['constmethod'] = False
    model.cc.MemberMethod(**kwargs)

    kwargs['parent'] = folder_element_access
    kwargs['name'] = 'back'
    kwargs['type'] = model.cc.typeinst(type=const_reference)
    kwargs['constmethod'] = True
    model.cc.MemberMethod(**kwargs)

    kwargs['parent'] = folder_element_access
    kwargs['name'] = 'data'
    kwargs['type'] = model.cc.typeinst(type=
    cached_type(parent.project, '@'), type_alias='T', const=True, ptr=True)
    kwargs['constmethod'] = False
    model.cc.MemberMethod(**kwargs)

    kwargs['parent'] = folder_element_access
    kwargs['name'] = 'data'
    kwargs['type'] = model.cc.typeinst(type=
    cached_type(parent.project, '@'), type_alias='T', const=True, ptr=True)
    kwargs['constmethod'] = True
    model.cc.MemberMethod(**kwargs)

    ## ## iterators
    kwargs['parent'] = folder_methods
    kwargs['name'] = 'iterators'
    folder_iterators = model.Folder(**kwargs)

    kwargs['parent'] = folder_iterators
    kwargs['name'] = 'begin'
    kwargs['type'] = model.cc.typeinst(type=iterator)
    kwargs['constmethod'] = False
    model.cc.MemberMethod(**kwargs)

    kwargs['parent'] = folder_iterators
    kwargs['name'] = 'begin'
    kwargs['type'] = model.cc.typeinst(type=const_iterator)
    kwargs['constmethod'] = True
    model.cc.MemberMethod(**kwargs)

    kwargs['parent'] = folder_iterators
    kwargs['name'] = 'cbegin'
    kwargs['type'] = model.cc.typeinst(type=const_iterator)
    kwargs['constmethod'] = True
    model.cc.MemberMethod(**kwargs)

    kwargs['parent'] = folder_iterators
    kwargs['name'] = 'end'
    kwargs['type'] = model.cc.typeinst(type=iterator)
    kwargs['constmethod'] = False
    model.cc.MemberMethod(**kwargs)

    kwargs['parent'] = folder_iterators
    kwargs['name'] = 'end'
    kwargs['type'] = model.cc.typeinst(type=const_iterator)
    kwargs['constmethod'] = True
    model.cc.MemberMethod(**kwargs)

    kwargs['parent'] = folder_iterators
    kwargs['name'] = 'cend'
    kwargs['type'] = model.cc.typeinst(type=const_iterator)
    kwargs['constmethod'] = True
    model.cc.MemberMethod(**kwargs)

    kwargs['parent'] = folder_iterators
    kwargs['name'] = 'rbegin'
    kwargs['type'] = model.cc.typeinst(type=iterator)
    kwargs['constmethod'] = False
    model.cc.MemberMethod(**kwargs)

    kwargs['parent'] = folder_iterators
    kwargs['name'] = 'rbegin'
    kwargs['type'] = model.cc.typeinst(type=const_iterator)
    kwargs['constmethod'] = True
    model.cc.MemberMethod(**kwargs)

    kwargs['parent'] = folder_iterators
    kwargs['name'] = 'crbegin'
    kwargs['type'] = model.cc.typeinst(type=const_iterator)
    kwargs['constmethod'] = True
    model.cc.MemberMethod(**kwargs)

    kwargs['parent'] = folder_iterators
    kwargs['name'] = 'rend'
    kwargs['type'] = model.cc.typeinst(type=iterator)
    kwargs['constmethod'] = False
    model.cc.MemberMethod(**kwargs)

    kwargs['parent'] = folder_iterators
    kwargs['name'] = 'rend'
    kwargs['type'] = model.cc.typeinst(type=const_iterator)
    kwargs['constmethod'] = True
    model.cc.MemberMethod(**kwargs)

    kwargs['parent'] = folder_iterators
    kwargs['name'] = 'crend'
    kwargs['type'] = model.cc.typeinst(type=const_iterator)
    kwargs['constmethod'] = True
    model.cc.MemberMethod(**kwargs)

    ## ## capacity
    kwargs['parent'] = folder_methods
    kwargs['name'] = 'capacity'
    folder_capacity = model.Folder(**kwargs)

    kwargs['parent'] = folder_capacity
    kwargs['name'] = 'fill'
    kwargs['type'] = model.cc.typeinst(type=
        cached_type(parent.project, 'void'))
    kwargs['constmethod'] = False
    fill = model.cc.MemberMethod(**kwargs)

    kwargs['parent'] = fill
    kwargs['name'] = 'value'
    kwargs['type'] = model.cc.typeinst(type=
        cached_type(parent.project, '@'), type_alias='T', const=True, ref=True)
    model.cc.Argument(**kwargs)

    kwargs['parent'] = folder_capacity
    kwargs['name'] = 'swap'
    kwargs['type'] = model.cc.typeinst(type=
        cached_type(parent.project, 'void'))
    swap = model.cc.MemberMethod(**kwargs)

    kwargs['parent'] = swap
    kwargs['name'] = 'other'
    kwargs['type'] = model.cc.typeinst(type=cls, ref=True)
    model.cc.Argument(**kwargs)

    # Create module for related globals
    kwargs['parent'] = array_folder
    kwargs['name'] = 'non-member-functions '
    non_members = model.cc.Module(**kwargs)

    for op in ['==', '!=', '<', '<=', '>', '>=']:
        kwargs['parent'] = non_members
        kwargs['name'] = 'operator {op}'.format(op=op)
        kwargs['template'] = 'class T, std::size_t N'
        kwargs['template_types'] = ['T']
        kwargs['type'] = model.cc.typeinst(type=cached_type(parent.project, 'bool'))
        operator = model.cc.Function(**kwargs)

        kwargs['parent'] = operator
        kwargs['name'] = 'lhs'
        kwargs['type'] = model.cc.typeinst(type=cls, const=True, ref=True)
        model.cc.Argument(**kwargs)

        kwargs['parent'] = operator
        kwargs['name'] = 'rhs'
        kwargs['type'] = model.cc.typeinst(type=cls, const=True, ref=True)
        model.cc.Argument(**kwargs)

    # Helpers
    kwargs['parent'] = array_folder
    kwargs['name'] = 'helper classes'
    helpers = model.Folder(**kwargs)

    kwargs['parent'] = helpers
    kwargs['name'] = 'tuple_size'
    kwargs['is_struct'] = False
    kwargs['template'] = 'class T, std::size_t N'
    kwargs['template_types'] = ['T']
    model.cc.Class(**kwargs)

    kwargs['parent'] = helpers
    kwargs['name'] = 'tuple_element'
    kwargs['template'] = 'std::size_t I, class T, std::size_t N'
    kwargs['template_types'] = ['T']
    model.cc.Class(**kwargs)

    #vector folder
    kwargs['parent'] = folder
    kwargs['name'] = 'vector'
    vector_folder = model.Folder(**kwargs)

    #std::vector
    kwargs['parent'] = vector_folder
    kwargs['name'] = 'vector'
    kwargs['template'] = 'class T, class Allocator = std::allocator<T>'
    kwargs['template_types'] = ['T']
    vector = model.cc.Class(**kwargs)


