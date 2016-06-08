# -*- coding: utf-8 -*-
import traceback
from malibu.design import borgish


__doc__ = """
malibu.command.module
---------------------

A relatively self-contained system for loading and creating command "modules"
for a CLI-style script.

A command module must extend the :class:`~malibu.command.module.CommandModule`
and set up the class as such:

.. code-block:: python

    from malibu.command import command_module, module

    @command_module(
        name = "example",
        depends = []
    )
    class ExampleModule(module.CommandModule):

        BASE = "example"

        def __init__(self, loader):

            super(ExampleModule, self).__init__()
            self.__loader = loader

            self.register_subcommand("help", self.show_help)

        def show_help(self, *args, **kw):
            \"\"\" example:help []

                Does something.
            \"\"\"

            if "args" in kw:
                argparser = kw["args"]
            else:
                argparser = self.__loader.get_argument_parser()

            pass  # Do stuff...


After all modules are implemented, use something similar to the following in
a console entry point:

.. code-block:: python

    from malibu import command
    from malibu.util import args

    argparser = args.ArgumentParser.from_argv()
    # Set up argparser params, mappings, etc here.

    modloader = module.CommandModuleLoader(argparser)

    mods = command.get_command_modules(package = __package__)
    # Or replace __package__ with your cmd module package path
    modloader.register_modules(mods.values())
    modloader.instantiate_modules()

    argparser.parse()

    modloader.parse_command(
        argparser.parameters[1],  # module base
        *argparser.parameters[1:],  # subcommand and args
        args = argparser)

.. autoclass:: CommandModuleLoader
   :members:

.. autoclass:: CommandModule
   :members:

.. autoexception:: CommandModuleException
   :members:
"""


class CommandModuleLoader(borgish.SharedState):

    def __init__(self, argparser, *args, **kw):
        """ Initializes a ModuleLoader object with a list for modules and
            sets the static __instance so the object is always accessible.
        """

        super(CommandModuleLoader, self).__init__(*args, **kw)

        if "state" not in kw:
            self.__modules = []
            self.__modclasses = []

            self.__argparser = argparser

    def register_module(self, cls):
        """ Registers a single module in the modloader list.

            Checks if any module instances in the module list
            and raises if an instance already exists.

            Otherwise, the module is instantiated, appended,
            and returned.
        """

        instances = filter(lambda mod: isinstance(mod, cls), self.__modules)
        if True in instances:
            raise CommandModuleException("Cannot re-register module %s" %
                                         (cls.__name__))

        if cls in self.__modclasses:
            raise CommandModuleException("Cannot re-register module %s" %
                                         (cls.__name__))

        self.__modclasses.append(cls)

    def register_modules(self, clslist):
        """ Registers a list of modules through subsequent calls to
            register_module().  Returns the list of instantiated
            modules.
        """

        [self.register_module(module) for module in clslist]

    def instantiate_modules(self, clslist=[]):
        """ Instantiates all module classes that are registered.
            ** Might perform dependency lookup as well.
        """

        deferred = []

        if clslist == []:
            clslist = self.__modclasses

        for cls in clslist:
            for dep in cls.depend_modules:
                if self.get_module_by_base(dep) is None:
                    deferred.append(cls)
                    break
            if cls in deferred:
                continue
            else:
                self.__modules.append(cls(self))

        if len(deferred) != 0:
            self.instantiate_modules(deferred)

    def deinit_modules(self):
        """ Runs __deinit__ on all registered modules.
        """

        for module in self.__modules:
            module.__deinit__()

    def get_argument_parser(self):
        """ Returns the argument parser that will be passed into
            functions that are called by the loader as command line
            parameters.
            Allows modules to access the parser during instantiation
            to change param modules, add help text, register aliases,
            etc.
        """

        return self.__argparser

    def get_module_by_base(self, modbase):
        """ Returns a module instance by the module's base name.
            Returns None if the named instance does not exist.
        """

        for module in self.__modules:
            if module.get_base().lower() == modbase.lower():
                return module

        return None

    @property
    def modules(self):
        """ Returns the list of modules.
        """

        return self.__modules

    def deregister_module(self, obj):
        """ Removes a module instance from the list of registered
            modules.
        """

        if obj not in self.__modules:
            return None

        return self.__modules.remove(obj)

    def parse_command(self, command, *args, **kw):
        """ Process a command and fire the function for the matching
            command and subcommand.  Returns the function execution
            result, if any.
        """

        try:
            command, subcommand = command.split(':')
        except:
            command, subcommand = ['help', 'show']
        for module in self.__modules:
            if not module.is_command(command):
                continue
            if (not module.has_subcommand(subcommand) and not
                    module.has_alias(subcommand)):

                continue
            try:
                result = module.execute_subcommand(subcommand, *args, **kw)
                return result
            except:
                traceback.print_exc()
                raise CommandModuleException(
                    "Exception occurred while executing a command: "
                    "[command=%s subcommand=%s args=%s kw=%s]" % (
                        command, subcommand, args, kw))


class CommandModule(object):
    """ Module superclass.  Abstracts away some parts of
        a command module to make implementation simpler.
        Should only be inherited, never instantiated by itself.
    """

    def __init__(self, base=None):
        """ Initializes a Module object with the command base,
            maps, and help dictionary.
        """

        self.__command_base = base

        self.__command_map = {}
        self.__command_alias_map = {}

        self.__command_help = {}

    def __deinit__(self):
        """ Used during "system" shutdown.  Perform clean up of
            module data and close any open parts of the system
            that should be properly deinitialized.
        """

        pass

    def is_command(self, command):
        """ Simple boolean-returning method used during command
            parsing.
        """

        return command == self.get_base()

    def has_subcommand(self, subcommand):
        """ Boolean-returning method for if this Module
            has registered a specific subcommand.
        """

        return subcommand in self.__command_map.keys()

    def has_alias(self, alias):
        """ Boolean-returning method for if this Module
            has registered a specific alias.
        """

        return alias in self.__command_alias_map.keys()

    def resolve_alias(self, alias):
        """ Resolves an alias to a subcommand and returns
            the subcommand.
        """

        try:
            return self.__command_alias_map[alias]
        except:
            return None

    def get_base(self):
        """ Returns the command base.
        """

        if self.__command_base:
            return self.__command_base
        elif self.__class__.BASE_NAME:
            return self.__class__.BASE_NAME

    def get_help(self):
        """ Returns the help dictionary for this
            module.
        """

        return self.__command_help

    def register_subcommand(self, subcommand, function, aliases=[]):
        """ Registers a subcommand and its help in
            the internal maps. Updates aliases, subcommands, etc.
        """

        if subcommand in self.__command_map:
            raise CommandModuleException("Subcommand is already registered")
        else:
            self.__command_map.update({subcommand: function})
            if not function.__doc__:
                self.__command_help.update({subcommand: None})
            else:
                self.__command_help.update({
                    subcommand:
                    '\n'.join(
                        [line.strip() for line in function.__doc__.splitlines()
                         if line.strip() is not '']
                    )
                })

        for alias in aliases:
            if alias in self.__command_alias_map:
                raise CommandModuleException(
                    "Alias is already registered for subcommand %s" %
                    (subcommand))
            else:
                self.__command_alias_map.update({alias: subcommand})

    def unregister_subcommand(self, subcommand):
        """ Removes a subcommand, all aliases, and all help
            from the internal maps.
        """

        if subcommand not in self.__command_map:
            raise CommandModuleException(
                "Tried to remove nonexistent subcommand %s" %
                (subcommand))

        self.__command_map.pop(subcommand)

        remove_aliases = []
        for alias, sub in self.__command_alias_map.items():
            if sub == subcommand:
                remove_aliases.append(alias)

        [self.__command_alias_map.pop(alias) for alias in remove_aliases]

    def execute_subcommand(self, subcommand, *args, **kw):
        """ Attempts to fire the subcommand with arguments,
            and keywords, may throw CommandModuleException.
        """

        if subcommand not in self.__command_map:
            if subcommand not in self.__command_alias_map:
                raise CommandModuleException(
                    "Tried to execute unknown subcommand %s" %
                    (subcommand))
            else:
                subcommand = self.resolve_alias(subcommand)

        try:
            # If this doesn't work, we've actually tried to execute an unknown
            # subcommand.
            func = self.__command_map[subcommand]
            func(*args, **kw)
        except IndexError:
            raise CommandModuleException(
                "Tried to execute unknown subcommand/alias %s" %
                (subcommand))


class CommandModuleException(Exception):
    """ Super special exception for modules.
    """

    def __init__(self, value):

        Exception.__init__(self)

        self.value = value

    def __str__(self):

        return repr(self.value)
