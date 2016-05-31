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
from enum import Enum


class AutoEnumNumber(Enum):
    """Enum class that automatically increments each enum, starting at 0.

    Attributes:
        * None.
    """

    def __new__(cls):
        """Increments enum.

        Adapted from https://docs.python.org/3/library/enum.html#autonumber.

        Args:
            * None.

        Returns:
            The new object whose value has automatically been incremented.
        """
        value = len(cls.__members__)
        obj = object.__new__(cls)
        obj._value_ = value
        return obj
