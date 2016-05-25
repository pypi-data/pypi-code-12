# -*- encoding: utf-8 -*-

import json

import py3o.types as types


class Py3oJSONDecoder(json.JSONDecoder):
    """A JSON decoder that parses values into :class:`.Py3oTypeMixin` instances.

    :param Py3oTypeConfig config: A py3o.types configuration.

    .. seealso:: :class:`json.JSONDecoder`
    """

    def __init__(self, config=None, *args, **kwargs):

        if config is None:
            config = {}
        if not isinstance(config, types.Py3oTypeConfig):
            config = types.Py3oTypeConfig(**config)
        self.config = config

        super(Py3oJSONDecoder, self).__init__(
            object_hook=self._py3o_object_hook, parse_int=config.integer,
            parse_float=config.float, *args, **kwargs
        )

    def _py3o_object_hook(self, dct):

        py3o_type = dct.get('_py3o')
        if py3o_type is None:
            return dct

        val = dct.get('val')
        if py3o_type == 'date':
            res = self.config.date.strptime(val, '%Y%m%d')
        elif py3o_type == 'time':
            res = self.config.time.strptime(val, '%H%M%S')
        elif py3o_type == 'dt':
            res = self.config.datetime.strptime(val, '%Y%m%d%H%M%S')
        else:
            raise ValueError(u"Unknown type {}".format(py3o_type))

        return res
