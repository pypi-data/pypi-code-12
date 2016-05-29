# -*- coding: utf-8 -*-
from decimal import Decimal
import datetime
import dj_database_url
import os
import urlparse


def combine_settings(settings_module, _locals):
    _locals.update(getattr(settings_module, 'REPLACE', {}))
    for k, v in getattr(settings_module, 'MERGE', {}).items():
        if isinstance(v, dict):
            _locals[k].update(v)
        else:
            _locals[k] += _locals[k].__class__(v)


def setup_database(varname, default=None, db_dict=None, db_dict_key='default'):
    """
    A wrapper around dj_database_url's config() method. Additional features:
    - Support for the django-mssql backend with the 'mssql' scheme
    - Arbitrary settings and options as querystring parameters
    - Option to set the databases dictionary directly (DATABASES should be passed to db_dict)

    Querystring parameters work as follow:
    - Prefix the parameter name with 'options__' to add to the 'OPTIONS' dictionary;
      otherwise, it will be interpreted as a database setting (such as ATOMIC_REQUESTS)
    - Parameter names are uppercased automatically, except for those beginning with 'options__' which are left as-is
    - Use a '__int' suffix to enable automatic typecasting
    - Values 'true', 'false' or 'none' as values will be translated to the corresponding constants
    
    If a default value is not supplied and the indicated environment variable is not found, db_dict will not be modified.
    """
    # TODO: (JFrancese) contribute back to dj_database_url
    if 'mssql' not in urlparse.uses_netloc:
        urlparse.uses_netloc.append('mssql')
    if 'pyodbc' not in urlparse.uses_netloc:
        urlparse.uses_netloc.append('pyodbc')
    dj_database_url.SCHEMES['mssql'] = 'sqlserver_ado'
    dj_database_url.SCHEMES['pyodbc'] = 'django_pyodbc'
    for scheme in dj_database_url.SCHEMES:
        if scheme not in urlparse.uses_query:
            urlparse.uses_query.append(scheme)
    url = str_from_env(varname, default)
    if not url:
        return None
    config = dj_database_url.parse(url)
    config['OPTIONS'] = {}
    query = urlparse.parse_qs(urlparse.urlparse(url).query)

    for k, v in query.items():
        k = k.strip()
        v = v[0]

        if k.lower().startswith('options__'):
            dict_to_use = config['OPTIONS']
            k = k[9:]
        else:
            dict_to_use = config
            k = k.upper()

        if k.lower().endswith('__int'):
            typecast = int
            k = k[:-5]
        else:
            typecast = None

        if v.strip().lower() == 'false':
            v = False
        elif v.strip().lower() == 'true':
            v = True
        elif v.strip().lower() == 'none':
            v = None
        elif typecast:
            v = typecast(v.strip())

        dict_to_use[k] = v

    if db_dict is not None:
        db_dict[db_dict_key] = config
    return config


def str_from_env(varname, default=None, decode='utf-8'):
    val = os.environ.get(varname, None)
    if val is None or val.strip() == '':
        return default
    elif val.strip().lower() == 'none':
        return None
    else:
        if decode:
            return val.decode(decode)
        else:
            return val


def bool_from_env(varname, default=None):
    val = os.environ.get(varname, '').strip().lower()
    if val == '':
        return default
    elif val == 'none':
        return None
    elif val in ('0', 'false', 'f', 'n', 'no', 'off'):
        return False
    else:
        return True


def int_from_env(varname, default=None):
    val = os.environ.get(varname, '').strip().lower()
    if val == '':
        return default
    elif val == 'none':
        return None
    else:
        return int(val)


def decimal_from_env(varname, default=None):
    val = os.environ.get(varname, '').strip().lower()
    if val == '':
        return default
    elif val == 'none':
        return None
    else:
        return Decimal(val)


def date_from_env(varname, default=None):
    val = os.environ.get(varname, '').strip().lower()
    if val == '':
        return default
    elif val == 'none':
        return None
    else:
        return datetime.datetime.strptime(val, '%Y-%m-%d').date()


def eval_from_env(varname, default=None):
    val = os.environ.get(varname, None)
    if val is None or val.strip() == '':
        return default
    else:
        return eval(val.decode('utf-8'))
