'''
Argument validator

    >>> arguments = ArgumentList([
    ...     Argument('foo', (int,)),
    ...     Argument('bar', (basestring,)),
    ... ])
    >>> arguments.validate({
    ...     'foo': 1,
    ...     'bar': 'baz',
    ... })
    >>> arguments.validate({
    ...     'foo': 1,
    ... })
    ArgumentException:
'''


import re
import six
import traceback
import copy
from woodstove import exceptions, log


__sentinel__ = object()


class ArgumentList(object):
    '''
    Argument container

    @ivar args: C{dict} of argument specifications.
    @type args: C{dict}
    '''
    def __init__(self, *arg_list):
        '''
        Setup the argument list by converting the L{arg_list} argument into a
        C{dict} keyed off the L{Argument.key} attribute.

        @keyword arg_list: List of L{Argument} objects that make up the list.
        '''
        self.args = dict()

        if arg_list:
            for arg in arg_list:
                self.args[arg.key] = arg

    def __str__(self):
        ''' '''
        out = "ArgumentList: %r\n" % self

        for arg in self.args.itervalues():
            out += str(arg) + "\n"

        return out

    def unknown(self, args):
        '''
        Check for arguments in the request that are not part of the argument
        list.

        @param args: The argument C{dict} passed in by the user.
        @raise ArgumentException: Raised if an unknown argument is found.
        '''
        unknown_args = [k for k in args if k not in self.args]
        
        if unknown_args:
            msg = "Unknown arguments in input: %r" % unknown_args
            raise exceptions.ArgumentException(msg)

    def filter(self, args):
        '''
        Filter out unknown arguments.

        @param args: The argument C{dict} passed in by the user.
        @return: Filtered argument C{dict}
        '''
        out = dict(args)
        unknown_args = [(k, out.pop(k))[0] for k in args if k not in self.args]

        if unknown_args:
            log.get_logger(__name__).debug(
                    "Filtered arguments: %r" % unknown_args)

        return out

    def validate(self, args, func=None, check_type=True, check_unknown=True):
        '''
        Verify that the L{args} C{dict} contains valid arguments based on
        this spec.

        @param args: The argument C{dict} passed in by the user.
        @keyword func: The function calling validate.
        @keyword check_type: Should the type of the passed in values be
            verified.
        @keyword check_unknown: Should extra arguments be considered an error.
        @raise ArgumentException: Raised if any argument does not match spec.
        '''
        if check_unknown:
            self.unknown(args)
        else:
            args = self.filter(args)

        for arg in self.args.itervalues():
            arg.check(args, func, check_type)

        return args

    def update(self, mapping):
        '''
        Add the contents of L{mapping} to this argument list.

        @param mapping: C{dict} of arguments to add.
        '''
        self.args.update(mapping)

    def __deepcopy__(self, memo):
        '''
        Deep copy an ArugmentList object.

        @param memo: Memo dict used by deepcopy function.
        @return: New copy of this ArugmentList
        '''
        new = type(self)()
        new.args = copy.deepcopy(self.__dict__, memo)
        return new


class Argument(object):
    '''
    Argument specification

    @ivar key: Name of argument.
    @ivar type: Iterable of valid types (or ArgumentList object).
    @ivar optional: Is the argument optional?
    @ivar desc: Description of the argument.
    @ivar default: Default value if none is passed.
    @ivar hooks: Validation callback functions.
    @ivar required_funcs: Callers that should raise exceptions if required
        arguments are missing.
    @ivar censor: Should argument value be scrubbed from log output.
    '''

    def __init__(self, key, type, optional=False, desc=None,
                 default=__sentinel__, regex=None, disable_type_check=False,
                 censor=False, cast=None):
        '''
        Setup argument instance.

        @param key: Name of argument
        @param type: Iterable of valid types (or ArgumentList object).
        @keyword optional: Is the argument optional?
        @keyword desc: Descpiption of the argument.
        @keyword default: Default value (implys L{optional})
        @keyword regex: Regular expression pattern.
        @keyword disable_type_check: disable the type check hook.
        @keyword censor: Should argument be censored in logs.
        @keyword cast: callable to cast argument with before checking.
        '''
        self.hooks = dict()
        self.required_funcs = None
        self.private = dict()
        self.key = key
        self.type = type
        self.desc = desc
        self.default = default
        self.censor = censor
        self.cast = cast
        self.regex = regex
        self.disable_type_check = disable_type_check

        if default is not __sentinel__ and not optional:
            optional = True

        self.optional = optional

        if isinstance(type, ArgumentList):
            self.hook(hook_recurse)
            return

        if not disable_type_check:
            self.hook(hook_type)

        if regex:
            self.hook(hook_regex, re.compile(regex))

    def __repr__(self):
        return u"%s(%r, %r)" % (self.__class__.__name__, self.key, self.type)

    def __str__(self):
        ''' '''
        return u"%s(%r, %r, optional=%r, desc=%r, default=%r, regex=%r, "\
                "disable_type_check=%r, censor=%r, cast=%r)" % (
                self.__class__.__name__, self.key, self.type, self.optional,
                self.desc, self.default, self.regex, self.disable_type_check,
                self.censor, self.cast)

    def hook(self, callback,  private=None, funcs=None):
        '''
        Add a validation callback

        @param callback: function to add to callback set
        @keyword private: data to be used by the callback
        @return:
        '''
        self.hooks[callback] = {
            'private': private,
            'funcs': funcs,
        }
        return self

    def unhook(self, callback):
        '''
        Remove a validation callbac

        @param callback: function to remove from callback set
        '''
        del self.hooks[callback]

    def check(self, args, func=None, check_type=True):
        '''
        Check L{args} for valid value for this argument.

        @param args: The arguments passed by the user.
        @keyword func: Function calling validate.
        @keyword check_type: Should types be verified.
        @raise ArgumentException: If any validation hook fails.
        '''
        try:
            arg = args[self.key]
        except KeyError:
            try:
                if func not in self.required_funcs:
                    return args
            except TypeError:
                pass

            if self.optional:
                if self.default is not __sentinel__:
                    args[self.key] = self.default
                return args

            raise exceptions.ArgumentException('Missing required argument: %s'
                                               % self.key)

        if self.cast is not None:
            try:
                arg = self.cast(arg)
            except Exception:
                log.get_logger(__name__).debug(traceback.format_exc())
                msg = 'Unable to cast argument %s to %r' % (self.key,
                                                            self.cast)
                raise exceptions.ArgumentException(msg)

        for hook, opts in six.iteritems(self.hooks):
            larg = '*' * 10 if self.censor else arg
            log.get_logger(__name__).debug("Calling hook %r(%r, %r, %r, %r)" % (
                hook, self, larg, func, check_type))

            if opts['funcs'] and func not in opts['funcs']:
                continue

            try:
                opts['check_type'] = check_type
                args[self.key] = hook(self, arg, func, opts)
            except exceptions.ArgumentException:
                raise
            except Exception:
                log.get_logger(__name__).error("Exception in hook %r: %s" % (
                    hook, traceback.format_exc()))
                raise exceptions.ArgumentException(
                    "Error in argument validation")

        return args


class String(Argument):
    ''' String argument '''
    def __init__(self, key, **kwargs):
        '''
        @param key:
        @param **kwargs: Additional arguments passed to L{Argument}
            constructor.
        '''
        super(String, self).__init__(key, six.string_types, **kwargs)


class Integer(Argument):
    ''' Integer Argument '''
    def __init__(self, key, **kwargs):
        '''
        @param key:
        @param **kwargs: Additional arguments passed to L{Argument}
            constructor.
        '''
        super(Integer, self).__init__(key, six.integer_types, **kwargs)


class Float(Argument):
    ''' Floating point Argument '''
    def __init__(self, key, **kwargs):
        '''
        @param key:
        @param **kwargs: Additional arguments passed to L{Argument}
            constructor.
        '''
        super(Float, self).__init__(key, (float,), **kwargs)


class Number(Argument):
    ''' Number argument '''
    def __init__(self, key, **kwargs):
        '''
        @param key:
        @param **kwargs: Additional arguments passed to L{Argument}
            constructor.
        '''
        super(Number, self).__init__(key, six.integer_types + (float,), **kwargs)


class Bool(Argument):
    ''' Boolean Argument '''
    def __init__(self, key, **kwargs):
        '''
        @param key:
        @param **kwargs: Additional arguments passed to L{Argument}
            constructor.
        '''
        super(Bool, self).__init__(key, (bool, int), **kwargs)


class Peewee(Argument):
    ''' Peewee ORM model argument '''
    def __init__(self, key, model, ignore_required=False, **kwargs):
        spec = peewee_to_spec(model, ignore_required)
        super(Peewee, self).__init__(key, spec, **kwargs)

class Hook(Argument):
    ''' Hook callback argument '''
    def __init__(self, key, hook, private=None, **kwargs):
        '''
        Callback hook helper class.

        @param key: Argument name.
        @param hook: Callback function to be called when this argument is
            verified.
        @keyword private: Data to be stored in the argument for the hook.
        @param **kwargs: Additional arguments passed to L{Argument}
            constructor.
        '''
        super(Hook, self).__init__(key, None, **kwargs)
        self.hook(hook, private)

    def check(self, args, func=None, _=None):
        '''
        Overrides L{Argument.check} to force check_type to be set False.

        @param args: User argument C{dict}.
        @keyword func: Function calling validate.
        @raise ArgumentException: Raised if the callback raises an exception.
        '''
        return super(Hook, self).check(args, func, False)


class List(Argument):
    ''' List Argument '''
    def __init__(self, key, subtype=None, **kwargs):
        '''
        @param key:
        @keyword subtype: Type of values contained in the list.
        @param **kwargs: Additional arguments passed to L{Argument}
            constructor.
        '''
        super(List, self).__init__(key, (list, tuple), **kwargs)
        self.subtype = subtype

        if subtype is not None:
            if isinstance(subtype, ArgumentList):
                self.hook(hook_seq_recurse, subtype)
            else:
                try:
                    _ = iter(subtype)
                    self.hook(hook_seq_type, subtype)
                except TypeError:
                    raise exceptions.InternalException('Invalid subtype: %r' %
                                                       subtype)


def peewee_to_spec(model, ignore_required=False, **kwargs):
    ''' Convert a peewee model into an Argument spec '''
    return Argument('foo', (None,))


def hook_recurse(spec, arg, func, opts):
    '''

    @param spec:
    @param arg:
    @param func:
    @param opts:
    @return:
    @raise ArgumentException:
    '''
    return spec.type.validate(arg, opts['check_type'])


def hook_type(spec, arg, func, opts):
    '''
    Verify that the type of L{arg} is in the list of allowed types.

    @param spec:
    @param arg:
    @param func:
    @param opts:
    @return:
    @raise ArgumentException:
    '''
    if opts['check_type'] is False:
        return arg

    for t in spec.type:
        if isinstance(arg, t):
            return

    raise exceptions.ArgumentException("%s: %r is not %r" % (spec.key,
                                       type(arg), spec.type))

    return arg


def hook_regex(spec, arg, func, opts):
    '''
    Verify that L{arg} matches this arguments L{regex} pattern.

    @param spec:
    @param arg:
    @param func:
    @param opts:
    @return:
    @raise ArgumentException:
    '''
    arg = unicode(arg)
    pattern = opts['private']

    if re.search(pattern, arg) is None:
        raise exceptions.ArgumentException("%s: %r does not match regex %s" % (
                                           spec.key, arg, pattern))

    return arg


def hook_seq_type(spec, arg, func, opts):
    '''
    Check the type of all the values in an iterable.

    @param spec: Argument specification
    @param arg: User passed argument
    @param func: Function calling validate.
    @param opts: Options for the hook.
    @return: The processed argument.
    @raise ArgumentException: Raised if argument does not match pattern.
    '''
    types = opts['private']
    for val in arg:
        arg_type = type(val)
        if arg_type not in types:
            raise exceptions.ArgumentException("%s: %r is not %r" % (spec.key,
                                               arg_type, types))

    return arg


def hook_seq_recurse(spec, arg, func, opts):
    '''
    Check the type of all the values in an iterable.

    @param spec: Argument specification
    @param arg: User passed argument
    @param func: Function calling validate.
    @param opts: Options for the hook.
    @return: The processed argument.
    @raise ArgumentException: Raised if argument does not match pattern.
    '''
    spec = opts['private']

    for i in xrange(len(arg)):
        arg[i] = spec.validate(arg[i], opts['check_type'])

    return arg
