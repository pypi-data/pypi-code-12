#!python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

if __name__ == '__main__':
    import zoid

    zoid.init()

    print("-"*80)
    print("%- 16s %- 15s %- 8s %s" % ("name", "ip", "port", "branch") )
    print("-"*80)
    for cfg in zoid.CONFIG.get_derived_nodes("server"):
        branch = cfg.get_value("beta")
        if branch is None:
            branch = zoid.MASTER_BRANCH
        print("%- 16s %- 15s %- 8s %s" % (cfg.name, cfg.get_value("ip"), cfg.get_value("port"), branch) )
