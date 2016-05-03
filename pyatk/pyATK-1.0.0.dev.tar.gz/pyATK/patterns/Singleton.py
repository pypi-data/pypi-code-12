# -*- coding: utf-8 -*-


class ASingleton:
    instance = None

    def __init__(self):
        raise NotImplementedError("Cannot instantiate an abstract class...")

    @classmethod
    def get_instance(cls):
        if ASingleton.instance is None:
            ASingleton.instance = ASingleton()
        return ASingleton.instance
