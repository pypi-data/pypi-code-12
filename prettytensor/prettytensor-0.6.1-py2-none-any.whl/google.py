# Copyright 2015 Google Inc. All Rights Reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Add any google specific ops.

see [README.md](https://github.com/google/prettytensor) for documentation.
see pretty_tensor_samples/ for usage examples.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


import tensorflow.google as tf

# pylint: disable=unused-import, wildcard-import
from prettytensor import *
from prettytensor import local_trainer
from prettytensor import bookkeeper
from prettytensor.google_bookkeeper import GoogleBookkeeper as Bookkeeper

bookkeeper.BOOKKEEPER_FACTORY = Bookkeeper
local_trainer.SESSION_MANAGER_FACTORY = tf.training.SessionManager

del tf
