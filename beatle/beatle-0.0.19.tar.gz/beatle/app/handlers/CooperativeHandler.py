# -*- coding: utf-8 -*-
"""
Este fuente implementa el gestor de cooperacion.
Una actividad puede ofrecer operaciones que pueden ser compartidas
con otras actividades, vistas o paneles.
La comparticion de estos recursos se realiza a través de un registro
de operaciones en el que se asocia un nombre unico de operacion a
un conjunto de recursos que pueden ser desde barras de herramientas,
elementos de menu u metodos invocables.

nombre de operacion: los nombres de operacion deben de ser unicos.
Se debe de evitar utilizar nombres que identifiquen al proveedor.

cada operacion registrada constituye un espacio de recursos puestos
a disposicion de los clientes, y que pueden ser utilizados por este
de forma selectiva, mediante la gestion.

"""


class CooperativeResource(object):
    """Implementa un recurso compartido"""

    def __init__(self, name, **kwargs):
        """Inicializa el recurso compartido"""
        self._name = name
        self._data = kwargs
        self._version = kwargs.get('version', [0, 0, 0])
        super(CooperativeResource, self).__init__()

    @property
    def version(self):
        """return the version"""
        return self._version

    @property
    def name(self):
        """return the name"""
        return self._name


class SharedToolbar(CooperativeResource):
    """Implementa una toolbar compartida"""
    def __init__(self, name, **kwargs):
        """Inicializa el recurso compartido"""
        super(SharedToolbar, self).__init__(name, **kwargs)


class Cooperation(object):
    """Declara la estructura de una cooperacion"""

    def __init__(self, name, acm=None):
        """Inicializa la cooperacion"""
        self._name = name
        self._acm = acm  # validador
        self._resource_list = {}
        super(Cooperation, self).__init__()

    def available(self, client):
        """Determina si la cooperacion esta disponible para el cliente"""
        if self._acm is None:
            return True
        if hasattr(self._acm, '__call__'):
            return self._acm(client)
        return bool(self._acm)

    def add(self, resource):
        """Anhade un recurso a la cooperacion"""
        if resource.name in self._resource_list:
            for k in self._resource_list[resource.name]:
                if k.version == resource.version:
                    raise RuntimeError('duplicated resource {name} with version {version}'.format(
                        name=resource.name,
                        version=resource.version))
            self._resource_list[resource.name].append(resource)
        else:
            self._resource_list[resource.name] = [resource]


class CooperativeHandler(object):
    """Implementa el gestor de recursos compartidos.
    Esta clase actua como un singleton, de modo que
    cualquier intento de instanciacion genera un error
    de runtime"""
    _cooperation = {}  # diccionario de cooperaciones registradas
    _key = {}  # claves de acceso a cooperacion

    def __init__(self):
        """Inicializacion: No esta permitida"""
        raise RuntimeError("CooperativeHandler is not instanciable")

    @classmethod
    def register(cls, name, acm=None, key=None):
        """Accede a un registro de cooperacion o lo crea.
        Si el registro de cooperacion no existe, se crea, y se
        le asocia el filtro de acceso suministrado. Si el registro de
        cooperacion ya existe, en caso de que tenga una acm
        no nula asociada, el parametro acm no debe ser nulo
        y debe hacer matching con la clave con la que fue
        registrada la cooperacion. En caso negativo, se genera
        un error de runtime"""
        if name not in cls._cooperation:
            cls._cooperation[name] = Cooperation(name, acm)
            cls._key[name] = key
        elif cls._key[name] != key:
            raise RuntimeError('access to cooperation {name} is not allowed'.format(name=name))
        return cls._cooperation[name]

