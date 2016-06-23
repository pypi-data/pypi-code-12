#
# Copyright 2016 BMC Software, Inc.
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
#
from tspapi import Measurement
from tspetl import ETLTool
from tspetl import ETLCollector
import csv
import time
import logging

logger = logging.getLogger(__name__)


class CSVCollector(ETLCollector):

    def __init__(self, sink, file_path, batch_count, skip_first_line):
        super(CSVCollector, self).__init__()

    def collect(self):
        pass


class CSVTool(ETLTool):
    def __init__(self):
        super(CSVTool, self).__init__()
        self._file_path = None
        self._batch_count = 1
        self._skip_first_line = False
        self._origin = None
        self._app_id = None
        logging.basicConfig(level=logging.DEBUG)

    @property
    def name(self):
        return 'csv'

    @property
    def help(self):
        return 'Import CSV file'

    def add_parser(self, sub_parser):
        super(CSVTool, self).add_parser(sub_parser)
        self._parser.add_argument('-f', '--file', dest='file_path', metavar="file_path",
                                  help="Path to file to import", required=False)
        self._parser.add_argument('-b', '--batch', dest='batch_count', metavar="batch_count",
                                  help="How many measurements to send in each API call", required=False)
        self._parser.add_argument('-o', '--origin', dest='origin', metavar="origin",
                                  help="Origin to associated with the measurements", required=False)
        self._parser.add_argument('-p', '--application-id', dest='app_id', metavar="id",
                                  help="Application Id to associate with the measurements", required=False)
        self._parser.add_argument('--skip-first-line', dest='skip_first_line', action="store_true",
                                  help="Skip header line in file")

    def handle_arguments(self, args):
        super(CSVTool, self).handle_arguments(args)

        if args.file_path is not None:
            self._file_path = args.file_path

        if args.batch_count is not None:
            self._batch_count = args.batch_count

        if args.skip_first_line is not None:
            self._skip_first_line = args.skip_first_line

        if args.origin is not None:
            self._origin = args.origin

        if args.app_id is not None:
            self._app_id = args.app_id

    def run(self, sink):
        metric = None
        value = None
        source = None
        timestamp = None
        app_id = self._app_id
        origin = self._origin
        first = self._skip_first_line
        # TODO: Only allow batch of one since the measurement API is broken for batch
        batch_count = 1
        row_count = 1
        properties = None
        if origin is not None or app_id is not None:
            properties = {}
            if origin is not None:
                properties['origin'] = self._origin
            if app_id is not None:
                properties['app_id'] = self._app_id

        with open(self._file_path) as f:
            reader = csv.reader(f)
            measurements = []
            for row in reader:
                logger.debug("row length: {0}".format(len(row)))

                if first:
                    header = ','.join(row)
                    logger.info("header: {0}".format(header))
                    first = False
                    row_count += 1
                    continue

                timestamp = int(time.time())
                if len(row) == 4:
                    metric = row[0]
                    value = row[1]
                    source = row[2]
                    timestamp = row[3]
                elif len(row) == 3:
                    metric = row[0]
                    value = row[1]
                    source = row[2]
                elif len(row) == 2:
                    metric = row[0]
                    value = row[1]
                else:
                    pass
                measurement = Measurement(metric=metric, value=value, source=source, timestamp=timestamp,
                                          properties=properties)
                logger.debug(measurement)
                measurements.append(measurement)
                if row_count % batch_count == 0:
                    logger.info("sending {0} measurements".format(len(measurements)))
                    sink.send_measurement(measurement)
                    measurements = []
                row_count += 1

