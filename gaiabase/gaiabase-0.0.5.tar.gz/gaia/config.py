# -*- coding: utf-8 -*-

import os, sys
import json, yaml

import ConfigParser

import gaia.base as base


class DictCfgParser(ConfigParser.ConfigParser):

    def as_dict(self):
        d = dict(self._sections)
        for k in d:
            d[k] = dict(self._defaults, **d[k])
            d[k].pop('__name__', None)
        return d

if "CAIYUN_ENV" in os.environ:
    gaia_env = os.environ["CAIYUN_ENV"]
else:
    gaia_env = "dev"

cfg_path = os.path.join(base.find_path(), 'conf', gaia_env)

def on_production():
    return gaia_env == "prod"

def on_stagging():
    return gaia_env == "stagging"

def on_dev():
    return gaia_env == "dev"

def load_config(fname):
    result = None
    try:
        filename, extname = os.path.splitext(fname)
        basename = os.path.basename(filename)
        fpath = os.path.join(cfg_path, fname)
        result = {}
        if extname == '.cfg' or extname == '.ini':
            config = DictCfgParser()
            config.read(fpath)
            result = config.as_dict()
        if extname == '.json':
            with open(fpath, 'r') as fcfg:
                if basename != 'app':
                    result[basename] = json.load(fcfg)
                else:
                    result = json.load(fcfg)
        if extname == '.yaml':
            with open(fpath, 'r') as fcfg:
                if basename != 'app':
                    result[basename] = yaml.load(fcfg)
                else:
                    result = yaml.load(fcfg)
    except Exception as e:
        pass
    return result

def main():
    try:
        fname = sys.argv[1]
        item = sys.argv[2]
        prop = sys.argv[3]
        cfg = load_config(fname)
        sys.stdout.write(str(cfg.get(item, prop)))
        sys.exit(0)
    except BaseException:
        sys.exit(-1)

if __name__ == "__main__":
    main()