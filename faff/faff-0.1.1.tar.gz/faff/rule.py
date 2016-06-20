#!/usr/bin/env python
from .core import core
from .targets import Target
from .option import Option
from .variable import Variable
from .exceptions import (
    InvalidTargetException,
)


class Rule(object):
    '''
    Rule decorator class.
    '''
    class _Rule(object):
        '''
        Internal rule class.
        '''
        def __init__(self, *args, **kwargs):
            # Decorator keyword arguments.
            self._name = kwargs.get('name')
            self._func = kwargs.get('func')
            self._description = kwargs.get('desc')

            # Optional rule dependencies (`depends` keyword argument).
            rule_depends = kwargs.get('depends', [])
            if isinstance(rule_depends, Target):
                self._rule_depends = [rule_depends]
            elif isinstance(rule_depends, list):
                self._rule_depends = rule_depends
            else:
                # TODO: More informational exception.
                core.raise_exception(
                    '`depends` is not an instance of `Target` class or a list',
                    cls=InvalidTargetException,
                )

            # Optional rule command line options (`options` keyword argument).
            rule_options = kwargs.get('options', [])
            if Option.is_opt(rule_options):
                self._rule_options = [rule_options]
            elif isinstance(rule_options, list):
                self._rule_options = rule_options
            else:
                # TODO: Subclassed exception, error message.
                raise Exception('invalid argument')

            # Targets and target dependencies.
            self._targets = []
            self._depends = []

            # Decorator positional arguments.
            for arg in args:
                # If argument is a Target instance, RulePattern2.
                if isinstance(arg, Target):
                    self._targets.append(arg)
                    self._depends.append(None)

                # Else if argument is list.
                elif isinstance(arg, list):
                    targets = arg[0] if len(arg) > 0 else None
                    depends = arg[1] if len(arg) > 1 else None

                    # If targets is a Target instance.
                    if isinstance(targets, Target):
                        self._targets.append(targets)

                        # If depends is a Target instance, RulePattern3.
                        if isinstance(depends, Target):
                            self._depends.append([depends])

                        # Else if depends is a list, RulePattern4.
                        elif isinstance(depends, list):
                            self._depends.append(depends)
                        else:
                            # TODO: Subclassed exception, error message.
                            raise Exception('invalid argument')

                    # Else if targets is a list of Target instances.
                    elif isinstance(targets, list):

                        # If depends is a Target instance, RulePattern5.
                        if isinstance(depends, Target):
                            for target in targets:
                                self._targets.append(target)
                                self._depends.append([depends])

                        # Else if depends is a list.
                        elif isinstance(depends, list):

                            # If lists are equal in length.
                            if len(targets) == len(depends):
                                for target, depend in zip(targets, depends):
                                    self._targets.append(target)

                                    # If depend is a Target instance,
                                    # RulePattern6.
                                    if isinstance(depend, Target):
                                        self._depends.append([depend])
                                    # Else if depend is a list, RulePattern8.
                                    elif isinstance(depend, list):
                                        self._depends.append(depend)
                                    # Else unknown depend argument.
                                    else:
                                        # TODO: Subclassed exception, message.
                                        raise Exception('invalid argument')

                            # Else, RulePattern7.
                            else:
                                for target in targets:
                                    self._targets.append(target)
                                    self._depends.append(depends)

                        # Else unknown depends argument.
                        else:
                            # TODO: Subclassed exception, error message.
                            raise Exception('invalid argument')

                    # Else unknown targets argument.
                    else:
                        # TODO: Subclassed exception, error message.
                        raise Exception('invalid argument')

                # Else unknown primary argument.
                else:
                    # TODO: Subclassed exception, error message.
                    raise Exception('invalid argument')

            # No arguments, RulePattern1.

            # Test internal data for correctness.
            # TODO: Refactor this.
            # Rule dependencies must be a list of Target instances.
            for depend in self._rule_depends:
                assert isinstance(depend, Target), 'TODO: not a Target'
            # Rule options must be a list of Option instances.
            for option in self._rule_options:
                assert Option.is_opt(option), 'TODO: not an Option'
            # Targets must be a list of Target instances.
            # Target dependencies must be a list of lists of Target instances.
            for target, depends in zip(self._targets, self._depends):
                assert isinstance(target, Target), 'TODO: not a Target'
                if depends is not None:
                    assert isinstance(depends, list), 'TODO: not a list'
                    for depend in depends:
                        assert isinstance(depend, Target), 'TODO: not a Target'

        def __call__(self):
            # Rule dependencies update override.
            upd_override = False

            # Ensure rule dependencies are up to date.
            for depend in self._rule_depends:
                if depend.out_of_date():
                    upd_override = True

            # If targets list is empty, always run function.
            if len(self._targets) == 0:
                try:
                    self._func(None, None)
                except KeyboardInterrupt:
                    # Assume target not updated if interrupted by user.
                    return (0, 1)
                else:
                    # Assume target updated (null target).
                    return (1, 1)

            # TODO: Concurrency using deco.
            # https://github.com/alex-sherman/deco
            # For each Target instance and dependencies list.
            target_depends_pairs = zip(self._targets, self._depends)
            updated = 0

            for i, target_depends in enumerate(target_depends_pairs):
                target, depends = target_depends

                # Save current automatic variables context.
                ctx = Variable.save_vars()

                # Use target class method to populate automatic variables.
                Target.set_vars(target, depends)

                # Use update override.
                upd = upd_override

                # Update if target does not exist.
                if target.out_of_date():
                    upd = True

                # Update if target out of date compared to dependencies.
                if depends is not None:
                    for depend in depends:
                        if target.out_of_date(depend):
                            upd = True

                # If update required, call rule function, increment counter.
                if upd:
                    # TODO: Move rule function call to method.
                    try:
                        self._func(target, depends)
                    except KeyboardInterrupt:
                        # Early return when interrupted by user.
                        return (updated, len(self._targets))
                    else:
                        updated += 1

                # Restore variable context.
                Variable.restore_vars(ctx)

            # Return number of updated and total.
            return (updated, len(self._targets))

        def add_options(self, parser):
            '''
            Add rule option arguments to parser.
            '''
            # For each option, add argument to parser.
            for opt in self._rule_options:
                opt.add_argument(parser)

        def call_options(self, args):
            '''
            Call rule options with arguments.
            '''
            # Call each option instance with parsed argument.
            for opt in self._rule_options:
                opt(getattr(args, opt.get_name()))

        def get_description(self):
            '''
            Get rule description.
            '''
            return self._description

        def get_targets(self):
            '''
            Get internal list of rule targets.
            '''
            return self._targets

    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs

    def __call__(self, func):
        # Use decorated function to create rule object.
        self._kwargs.setdefault('name', func.__name__)
        self._kwargs.setdefault('func', func)
        self._kwargs.setdefault('desc', func.__doc__)
        return self._Rule(*self._args, **self._kwargs)

    @staticmethod
    def is_rule(obj):
        '''
        Test if object is a rule (instance of Rule._Rule).
        '''
        if isinstance(obj, Rule._Rule):
            return True
        return False
