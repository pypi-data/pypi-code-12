## DTSettingsConfig
#
# Copyright (c) 2016, Expressive Analytics, LLC <info@expressiveanalytics.com>.
# All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# @package Deep Thought
# @author Blake Anderson <blake@expressiveanalytics.com>
# @copyright 2016 Expressive Analytics, LLC <info@expressiveanalytics.com>
# @licence http://choosealicense.com/licenses/mit
# @link http://www.expressiveanalytics.com
# @since version 1.0.0

from .DTSettings import DTSettings
import json
import os

class DTSettingsConfig(DTSettings):
    _shared_config = {}

    @classmethod
    def initShared(cls,path):
        cls._shared_config = json.load(open(path))
        return cls._shared_config

    @classmethod
    def sharedSettings(cls,settings=None):
        if settings is not None:
            cls._shared_config.update(settings)
        return cls._shared_config

    @classmethod
    def baseURL(cls,suffix=""):
        base = ""
        if "base_url" in cls._shared_config:
            base = cls._shared_config["base_url"]
        elif "HTTP_HOST" in os.environ:
            base = os.environ["HTTP_HOST"]
        if base[-1:] != "/":
            base += "/"
        if base == "/":
            return "/"+suffix
        return "{}://{}{}".format("https" if "HTTPS" in os.environ != "off" else "http",base,suffix)
