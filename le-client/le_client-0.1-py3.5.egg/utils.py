# This file is part of le_client.
#
# le_client is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# le_client is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with le_client.  If not, see <http://www.gnu.org/licenses/>.

import subprocess
import base64


def b64(data):
    return base64.urlsafe_b64encode(data).decode("utf-8").replace("=", "")


def first(iterable, default=None):
    if iterable:
        for item in iterable:
            return item
    return default


def openssl(*args, stdin=None):
    process = subprocess.Popen(
        ["openssl"] + list(args),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    out, err = process.communicate(stdin)
    if process.returncode != 0:
        raise IOError("OpenSSL error: {}".format(err.decode("utf-8")))
    return out
