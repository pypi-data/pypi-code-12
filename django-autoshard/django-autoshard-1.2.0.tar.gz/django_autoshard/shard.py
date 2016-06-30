from django.db import connections


class Shard:
    def __init__(self, index, alias, replicas):
        self.__index = index
        self.__alias = alias
        self.__replicas = replicas

    @property
    def alias(self):
        return self.__alias

    @property
    def index(self):
        return self.__index

    @property
    def connection(self):
        return connections[self.alias]

    @property
    def database(self):
        return self.connection.settings_dict['NAME']

    @property
    def host(self):
        return self.connection.settings_dict['HOST']

    def __str__(self):
        return self.alias
