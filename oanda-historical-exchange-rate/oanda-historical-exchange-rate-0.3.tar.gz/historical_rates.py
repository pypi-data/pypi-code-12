# coding=utf-8
from csv import reader
from requests import get


class Currency:

    def __init__(self, from_currency, to_currency, period='daily'):

        self.base_url = 'http://www.oanda.com/currency/historical-rates/download?display=absolute&rate=0&data_range=c&price=mid&view=table'
        self.base_url += '&quote_currency={from_currency}&base_currency_0={to_currency}&period={period}&download=csv'
        self.from_currency = from_currency
        self.to_currency = to_currency
        self.period = period
        self.url = self.base_url.format(
            from_currency=from_currency, to_currency=to_currency, period=period
        )

    def historical(self, start_date, end_date, raw=False):

        dictionary_list = []

        url = self.url + '&start_date={start_date}&end_date={end_date}'.format(
            start_date=start_date, end_date=end_date
        )

        csv_http = get(url)
        csv_object = reader(csv_http.text, delimiter=',')

        if raw is False:
            j = 1
            for row in csv_object:
                if not len(row) == 0 and not '' in row:
                    if j % 2 != 0:
                        temporary_dict = {}
                        temporary_dict['date'] = row[0]
                    else:
                        temporary_dict['value'] = row[0]
                        dictionary_list.append(temporary_dict)
                    j += 1

            dictionary_list.sort(key=lambda x: x['date'])
            dictionary_list = dictionary_list[:len(dictionary_list) - 5]
        else:
            return csv_object

        return dictionary_list
