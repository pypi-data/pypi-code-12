#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2013,2014,2016 Jérémie DECOCK (http://www.jdhp.org)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import argparse
import feedparser

YAHOO_CITY_CODES_DICT = {
    'cergy': '583634',
    'orsay':'55863553',
    'paris': '615702'
    }

def weather_yahoo(city):
    weather_str_tuple = ("-", "")

    if city in YAHOO_CITY_CODES_DICT:
        rss_url = "http://weather.yahooapis.com/forecastrss?w=" + YAHOO_CITY_CODES_DICT[city] + "&u=c"
        feed_dict = feedparser.parse(rss_url)

        location_dict   = feed_dict.feed.yweather_location   # contains the locations dictionary
        atmosphere_dict = feed_dict.feed.yweather_atmosphere # contains the atmospheric conditions dictionary (pressure/humidity)
        astronomy_dict  = feed_dict.feed.yweather_astronomy  # contains the astronomy dictionary (sunset/sunrise hours)
        summary_list = feed_dict.entries[0].summary.splitlines()

        city = location_dict['city']
        humidity = atmosphere_dict['humidity']
        pressure = atmosphere_dict['pressure']
        sunrise = astronomy_dict['sunrise']
        sunset = astronomy_dict['sunset']
        weather_pic = summary_list[0].split("<br />")[0].split("\"")[1]
        current_conditions = summary_list[2].split("<br />")[0][:-2]
        current_conditions, current_temp = current_conditions.split(",")
        current_conditions = current_conditions.strip()
        current_temp = current_temp.strip()
        today_forecast, today_forecast_temp = summary_list[4].split("<br />")[0].split(" - ")[1].split(". ")
        today_forecast_temp_list = today_forecast_temp.split()
        today_forecast_temp_max = today_forecast_temp_list[1]
        today_forecast_temp_min = today_forecast_temp_list[3]

        #print city
        #print "humidity", humidity
        #print "pressure", pressure
        #print "sunrise", sunrise
        #print "sunset", sunset
        #print weather_pic
        #print current_conditions
        #print today_forecast, today_forecast_temp

        current_conditions_str = current_conditions.lower() + " (" + current_temp + u"°C)"
        today_forecast_str = today_forecast.lower() + " (" + today_forecast_temp_min + u"°C / " + today_forecast_temp_max + u"°C)"

        weather_str_tuple = (current_conditions_str, today_forecast_str)

    return weather_str_tuple


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="...")
    parser.add_argument("arg", nargs=1, metavar="STRING",
                        help="...")

    args = parser.parse_args()

    print(weather_yahoo(args.arg[0]))

