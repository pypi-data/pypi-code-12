#
# Copyright 2016 BMC Software, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from requests.structures import LookupDict

_aggregates = {

    'avg': ('AVG',),
    'min': ('MIN',),
    'max': ('MAX',),
    'sum': ('SUM',),
}

aggregates = LookupDict(name='aggregates')

for code, titles in _aggregates.items():
    for title in titles:
        setattr(aggregates, title, code)
        if not title.startswith('\\'):
            setattr(aggregates, title.upper(), code)
