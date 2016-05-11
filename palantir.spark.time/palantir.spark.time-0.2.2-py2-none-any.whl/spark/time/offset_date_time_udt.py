#
# Copyright 2016 Palantir Technologies, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import division

import pytz
from pyspark.sql.types import IntegerType, TimestampType, StructField, StructType, UserDefinedType


SECONDS_PER_MINUTE = 60

class OffsetDateTimeUdt(UserDefinedType):
    """
    SQL user-defined type (UDT) for OffsetDateTime, which is a wrapper around datetime.datetime
    Consists of a timestamp (datetime.datetime) and a zone offset in seconds (int).
    """

    @classmethod
    def sqlType(cls):
        return StructType([
            StructField("timestamp", TimestampType(), False),
            StructField("offset", IntegerType(), False)])

    @classmethod
    def module(cls):
        return "palantir.spark.time.offset_date_time_udt"

    @classmethod
    def scalaUDT(cls):
        return "com.palantir.spark.time.OffsetDateTimeUdt"

    def simpleString(self):
        return "offsetdatetimeudt"

    def serialize(self, obj):
        if isinstance(obj, OffsetDateTime):
            simple_dt = obj.simple_dt.replace(tzinfo=pytz.UTC)
            return (simple_dt, obj.offset)
        else:
            raise TypeError("cannot serialize type %r" % (type(obj),))

    def deserialize(self, datum):
        if len(datum) != 2:
            raise Exception("OffsetDateTimeUdt.deserialize given with length %d but requires 2" % len(datum))
        timestamp, offset = datum
        return OffsetDateTime(timestamp, offset)

    def __eq__(self, other):
        return other is not None and type(self) == type(other)


class OffsetDateTime(object):
    """
    Contains the DateTime with no timezone information and the timezone offset in seconds.
    We can't directly use datetime because PySpark will use TimestampType for it.
    """

    __UDT__ = OffsetDateTimeUdt()

    def __init__(self, dt, offset):
        self.simple_dt = dt.replace(tzinfo=None)
        self.offset = offset

    @classmethod
    def fromDateTimeWithTimeZone(cls, dt):
        if dt.tzinfo is None:
            raise Exception("Datetime object to be converted must have a not None tzinfo field.")
        simple_dt = dt.replace(tzinfo=None)
        offset = dt.utcoffset().total_seconds()
        return OffsetDateTime(simple_dt, offset)

    def toDateTime(self):
        return self.simple_dt.replace(tzinfo=pytz.FixedOffset(self.offset // SECONDS_PER_MINUTE))
