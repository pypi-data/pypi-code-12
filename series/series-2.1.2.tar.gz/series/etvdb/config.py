from tek.config import PathConfigOption
from tek.config.options import DictConfigOption

metadata = dict(parents=['series'])


def reset_config():
    return {
        'etvdb': dict(
            path=PathConfigOption('/usr/bin/etvdb',
                                  help='etvdb executable path'),
            series_name_map=DictConfigOption(),
        )
    }


__all__ = ['reset_config', 'metadata']
