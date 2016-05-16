# -*- coding: utf-8 -*-
"""
Copyright (C) 2015, MuChu Hsu
Contributed by Muchu Hsu (muchu1983@gmail.com)
This file is part of BSD license

<https://opensource.org/licenses/BSD-3-Clause>
"""
import story_chain.flaskrunner as flaskrunner
def entry_point():
    flaskrunner.start_flask_server()

if __name__ == "__main__":
    entry_point()