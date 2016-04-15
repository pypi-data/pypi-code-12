import os
import json
from .locale import en, zh_CN
from .util import config

def msg():
    lang = get_lang()
    if lang=='zh':
        lang='zh_CN'
    return eval('%s.getJSON()' % lang)

def get_lang(default_lang='zh_CN'):
    m = config.getConfigs(config.COMMON, ['locale'])
    if m and m.get('locale'):
        return m['locale']
    else:
        return default_lang

def get_lang3(default_lang):
    usr_home = os.path.expanduser('~')
    cfg_dir = os.path.join(usr_home, '.batchcompute')
    try:
        with open(os.path.join(cfg_dir, 'cliconfig.json')) as f:
            st = f.read()
            obj = json.loads(st)
            return obj.get('locale') or default_lang
    except IOError as e:
        return default_lang
