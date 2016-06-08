# -*- coding: utf-8 -*-

__doc__ = """
malibu.design.borgish
---------------------

Borgish was designed as a more extended implementation of Alex Martelli's
Borg design pattern, which aims to provide state consistency similar to
a singleton design, but without the terribleness of singletons.
"""


class SharedState(object):
    """ This class is for meta-class use as a state machine for
        persistence so we don't use any singleton design.

        The module is "Borg-ish", as this implementation is loosely
        based on the Borg design pattern by Alex Martelli.
    """

    @classmethod
    def __initialize_states(cls):
        """ Initializes a class-scoped states dictionary to store named
            states.
        """

        if not hasattr(cls, "_SharedState__states"):
            cls.__states = {}

    def __init__(self, *args, **kw):
        """ Calls the classes state dict initializer and loads initial
            state, if provided.
        """

        self.__initialize_states()

        if "state" in kw:
            self.load_state(kw.get("state"))

    def load_state(self, state):
        """ Loads state into the class, overwriting all data that was
            previously stored.

            :param str state: Name of state to load.
            :rtype: None
            :returns: None
            :raises NameError: If the named state does not exist.
        """

        if state in self.__states:
            self.__dict__ = self.__states[state]
        else:
            raise NameError("Can't load non-existent state '%s'." % (state))

    def save_state(self, state):
        """ Saves class state into a namespace on the class' shared state
            dict.

            :param str state: Name of state to save.
            :rtype: None
            :returns: None
            :raises NameError: If the named state already exists.
        """

        if state in self.__states:
            raise NameError("Can't overwrite stored state '%s'." % (state))
        self.__states.update({state: self.__dict__})
