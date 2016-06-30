#   Copyright 2016 University of Lancaster
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import logging
import subprocess


def check_cmd_log_output(args):
    return_code = 0

    logging.info("Launching command: {!r}".format(args))

    try:
        output = subprocess.check_output(
            args, stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        return_code = e.returncode
        output = e.output

    logging.info(output)

    msg = "Command completed with return code {}".format(return_code)

    if return_code == 0:
        logging.info(msg)
        return True

    logging.warning(msg)
    return False
