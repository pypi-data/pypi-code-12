#!/usr/bin/python3


class AStrategy:
    def __init__(self):
        self.callback = None
        raise NotImplementedError("Cannot instantiate an abstract class...")
    
    def execute(self, *args, **kwargs):
        if callable(self.callback) is True:
            return self.callback(*args, **kwargs)
        else:
            raise TypeError(self.callback.__name__ + " is not callable")
    
    def set_callback(self, callback):
        self.callback = callback 


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
