#!/usr/bin/env python
"""Gets stock quotes and other information for stock symbols.

The script can print real-time or close to real-time stock quotes, historical
quotes, and also fundamental ratios for the stock (company).

TODO:
Use google api instead, e.g. http://www.google.com/finance/info?q=nasdaq:appl


    Copyright 2014 Heung Ming Tai

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import argparse

from cStringIO import StringIO

import csv
import datetime
import logging
import sys
import subprocess

from bs4 import BeautifulSoup
import requests
from sorno import loggingutil
from sorno import consoleutil

_LOG = logging.getLogger(__name__)
_PLAIN_LOGGER = None  # will be created in main()
_PLAIN_ERROR_LOGGER = None  # will be created in main()


class StockApp(object):
    # https://code.google.com/p/yahoo-finance-managed/wiki/enumQuoteProperty
    FIELD_HEADERS = [
        ("name", "s"),
        ("price", "l1"),
        ("date", "d1"),
        ("time", "t1"),
        ("change", "c1"),
        ("changeInPercent", "c"),
        ("lastTradeRealtime", "k1"),
        ("changeRealtime", "c6"),
        ("changePercentRealtime", "k2"),
        ("open", "o"),
        ("high", "h"),
        ("low", "g"),
        ("volume", "v"),
        ("AverageDailyVolume", "a2"),
        # ("SharesOutstanding", "j2"), shares outstanding returns non-standard
        # csv value
        ("bidRealtime", "b3"),
        ("askRealtime", "b2"),
        ("YearLow", "j"),
        ("YearHigh", "k"),
        ("DilutedEPS", "e"),
        ("EPSEstimateCurrentYear", "e7"),
        ("EPSEstimateNextYear", "e8"),
        ("PERatio", "r"),
        ("PERatioRealtime", "r2"),
        ("ShortRatio", "s7"),
        ("DividendPayDate", "r1"),
        ("ExDividendDate", "q"),
    ]

    YAHOO_STOCK_QUOTE_CSV_API = "http://download.finance.yahoo.com/d/quotes.csv"
    YAHOO_STOCK_HISTORICAL_QUOTES_API = "http://ichart.yahoo.com/table.csv"
    YAHOO_STOCK_INSIDER_PURCHASES_PAGE_TEMPLATE = (
        "http://finance.yahoo.com/q/it?s=%s+Insider+Transactions"
    )

    QUANDL_STOCK_FUNDAMENTAL_API = "http://www.quandl.com/api/v1/datasets/OFDP/DMDRN_%s_ALLFINANCIALRATIOS.csv"

    def __init__(
        self,
        stock_symbol,
        print_fundamentals=False,
        print_history=False,
        print_price_quote=True,
        num_of_days_for_history=30,
        print_insider_purchases=False,
    ):
        self.stock_symbol = stock_symbol

        self.print_fundamentals = print_fundamentals
        self.print_history = print_history
        self.print_price_quote = print_price_quote

        self.num_of_days_for_history = num_of_days_for_history
        self.print_insider_purchases = print_insider_purchases

    def run(self):
        if self.print_price_quote:
            resp = requests.get(
                self.YAHOO_STOCK_QUOTE_CSV_API,
                params={
                    's': self.stock_symbol,
                    'f': "".join([h[1] for h in self.FIELD_HEADERS]),
                    'e': ".csv",
                },
            )
            _LOG.debug("URL: %s", resp.url)

            text = resp.text.strip()
            headers = [h[0] for h in self.FIELD_HEADERS]

            lines = [",".join(headers), text]
            reader = csv.DictReader(lines)
            # there is only one row in the result
            d = list(reader)[0]

            for header in headers:
                _PLAIN_LOGGER.info("%s:\t%s", header, d[header])

        if self.print_fundamentals:
            resp = requests.get(
                self.QUANDL_STOCK_FUNDAMENTAL_API % self.stock_symbol.upper()
            )

            text = resp.text

            reader = csv.DictReader(text.split("\n"))

            rows = list(reader)
            rows.sort(key=lambda r: r['Date'])

            consoleutil.DataPrinter(rows).print_result(
                consoleutil.DataPrinter.PRINT_STYLE_VERBOSE
            )

        if self.print_history:
            _PLAIN_LOGGER.info("")
            self.print_historical_stock_quotes()

        if self.print_insider_purchases:
            _PLAIN_LOGGER.info("")
            self.print_insider_purchase_entries()

    def print_historical_stock_quotes(self):
        today = datetime.datetime.today()
        from_date = today - datetime.timedelta(self.num_of_days_for_history)

        params = {
            's': self.stock_symbol,
            'a': from_date.month - 1,
            'b': from_date.day,
            'c': from_date.year,
            'd': today.month-1,
            'e': today.day,
            'f': today.year,
            'g': "d",  # daily quotes
            'ignore': ".csv",
        }

        resp = requests.get(
            self.YAHOO_STOCK_HISTORICAL_QUOTES_API,
            params=params,
        )

        _LOG.info("URL: %s", resp.url)

        for line in resp.text.split("\n"):
            _PLAIN_LOGGER.info(line.replace(",", "\t"))

    def print_insider_purchase_entries(self):
        resp = requests.get(
            self.YAHOO_STOCK_INSIDER_PURCHASES_PAGE_TEMPLATE % self.stock_symbol,
        )
        soup = BeautifulSoup(resp.text, "lxml")
        tables = soup.select("table.yfnc_tableout1")
        if len(tables) < 3:
            _PLAIN_ERROR_LOGGER.error("No insider purchases available")
            return 1

        insider_history_table = tables[2]

        headers = []
        rows = []
        for i, tr in enumerate(insider_history_table.select("tr table tr")):
            if i == 0:
                # process headers
                for th in tr.select("th"):
                    headers.append(th.get_text())
            else:
                # process data
                rows.append([td.get_text() for td in tr.select("td")])
        consoleutil.DataPrinter(
            rows,
            headers=headers,
            print_func=_PLAIN_LOGGER.info,
        ).print_result(consoleutil.DataPrinter.PRINT_STYLE_NICETABLE)


def parse_args(cmd_args):
    description = __doc__.split("Copyright 2014")[0].strip()

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--debug",
        action="store_true",
    )

    parser.add_argument(
        "--fundamentals",
        action="store_true",
        help="Print fundamentals data",
    )

    parser.add_argument(
        "--insider-purchases",
        action="store_true",
        help="Print insider purchases",
    )

    parser.add_argument(
        "--history",
        help="Print historical stock quotes",
        action="store_true",
    )

    parser.add_argument(
        "--no-price-quote",
        action="store_true",
        help="Not printing price quote of the stock",
    )

    parser.add_argument(
        "-n",
        "--num-of-days",
        help="Number of days to print for historical stock quotes",
        type=int,
        default=30,
    )

    parser.add_argument("stock_symbol", nargs="+")

    args = parser.parse_args(cmd_args)
    return args


def main():
    global _PLAIN_LOGGER, _PLAIN_ERROR_LOGGER

    args = parse_args(sys.argv[1:])

    loggingutil.setup_logger(_LOG, debug=args.debug)
    _PLAIN_LOGGER = loggingutil.create_plain_logger("PLAIN")
    _PLAIN_ERROR_LOGGER = loggingutil.create_plain_logger("PLAIN_ERROR", stdout=False)

    for stock_symbol in args.stock_symbol:
        app = StockApp(
            stock_symbol,
            print_history=args.history,
            print_price_quote=not args.no_price_quote,
            print_fundamentals=args.fundamentals,
            num_of_days_for_history=args.num_of_days,
            print_insider_purchases=args.insider_purchases,
        )
        app.run()


if __name__ == '__main__':
    main()
