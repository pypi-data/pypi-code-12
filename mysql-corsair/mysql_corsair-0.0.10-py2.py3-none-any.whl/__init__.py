from pkg_resources import get_distribution

__version__ = get_distribution('mysql-corsair').version

__all__ = ['commands', 'models', 'sql_query_helpers']
