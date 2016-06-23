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
from time import sleep
import string
from tspetl import ETLCollector
from tspetl import ETLTool
import pyowm
from tspapi import Measurement


class WeatherCollector(ETLCollector):
    def __init__(self, sink, api_key=None, cities=None):
        super(WeatherCollector, self).__init__(sink)

        self._api_key = None
        self._cities = None

        if api_key is not None:
            self._api_key = api_key
        if cities is not None:
            self._cities = cities

        self._owm = pyowm.OWM(self._api_key)

    def collect(self):
        measurements = []
        for city in self._cities:
            observation = self._owm.weather_at_place(city)
            weather = observation.get_weather()
            city = string.replace(city, ',', '_')
            city = string.replace(city, ' ', '_')
            temperature = weather.get_temperature('celsius')['temp']
            measurement = Measurement(metric='OWM_TEMPERATURE', source=city, value=temperature)
            measurements.append(measurement)

        self._sink.send_measurements(measurements=measurements)


class WeatherTool(ETLTool):
    def __init__(self):
        super(WeatherTool, self).__init__()
        self._city_names = None
        self._interval = 60
        self._api_key = None

    @property
    def name(self):
        return 'weather'

    @property
    def help(self):
        return 'Collects weather measurements from a city and optional country code. (Future Release)'

    def add_parser(self, sub_parser):
        super(WeatherTool, self).add_parser(sub_parser)
        self._parser.add_argument('-c', '--city-name', dest='city_names', action='append', metavar="city_name",
                                  required=True,
                                  help="Name of a city with an optional country code")
        self._parser.add_argument('-i', '--interval', dest='interval', action='store', metavar="seconds",
                                  required=False,
                                  help="How often to collect in each API call in seconds. Defaults to 1 minute")
        self._parser.add_argument('-k', '--api-key', dest='api_key', action='store', metavar="key", required=True,
                                  help="Open Weather Map API Key")

    def handle_arguments(self, args):
        super(WeatherTool, self).handle_arguments(args)

        if args.city_names is not None:
            print(type(args.city_names))
            self._city_names = args.city_names

        if args.interval is not None:
            self._interval = args.interval

        if args.api_key is not None:
            self._api_key = args.api_key

    def run(self, sink):
        collector = WeatherCollector(sink, cities=self._city_names, api_key=self._api_key)

        while True:
            collector.collect()
            sleep(float(self._interval))
