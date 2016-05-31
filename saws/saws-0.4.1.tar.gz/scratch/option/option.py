# -*- coding: utf-8 -*-

# Copyright 2015 Donne Martin. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

from __future__ import unicode_literals
from __future__ import print_function
from abc import ABCMeta, abstractmethod


class Option():
    """Encapsulates an AWS Option.

    Abstract base class for options.

    Attributes:
        * OPTION: A string representing the option that will cause the option
            completions to be displayed when typed.
        * HEADER: A string representing the header in the OPTIONS.txt file
            that denote the start of the given options.
        * options: A list of option.
    """

    __metaclass__ = ABCMeta

    OPTION = ''
    HEADER = ''

    def __init__(self):
        """Initializes Option.

        Args:
            * None.

        Returns:
            None.
        """
        self.options = []
        self.HEADER = '[' + self.OPTION + ']'

    @abstractmethod
    def get_options(self):
        pass
