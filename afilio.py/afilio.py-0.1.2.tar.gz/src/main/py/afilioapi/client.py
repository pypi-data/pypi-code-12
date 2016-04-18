import requests
import json


class AfilioSalesAPI():
    """
    Sales & Leads endpoint
    http://v2.afilio.com.br/api/leadsale_api.php?
         type=sale|lead
        &mode=list
        &token=<affiliate api token>
        &affid=<affiliate id>
        &dateStart=<filter begin> (format: YYYY-MM-DD)
        &dateEnd=<filter end> (format: YYYY-MM-DD)
        &format=xml|json|csv|rss (default: json)
    """
    LEADS = "lead"
    SALES = "sale"

    def __init__(self, token, affiliate_id):
        self.token = token
        self.affiliate_id = affiliate_id
        self.url_base = "http://v2.afilio.com.br/api/leadsale_api.php"

    def _build_params(self, report_type, date_start, date_end, program_id=None):
        if not report_type in [AfilioSalesAPI.LEADS, AfilioSalesAPI.SALES]:
            raise ValueError("Use one of valid report type: AfilioSalesAPI.LEADS (lead) or AfilioSalesAPI.SALES (sale)")

        params = dict(mode="list",
                      format="json",
                      token=self.token,
                      affid=self.affiliate_id,
                      type=report_type,
                      dateStart=date_start,
                      dateEnd=date_end,
                      progid=program_id,
                      )
        return params

    def _load(self, report_type, date_start, date_end, program_id=None):
        params = self._build_params(report_type, date_start, date_end, program_id)
        report = requests.get(self.url_base, params=params)
        return report.json()

    def get_report(self, report_type, date_start, date_end, program_id=None):
        return self._load(report_type, date_start, date_end, program_id)


class DateFormat():
    def __call__(self, value):
        import re
        format_rex = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
        date_parts = format_rex.findall(value)

        if not date_parts:
            raise ValueError("Invalid date format. Expected format is YYYY-MM-DD")

        year, month, day = date_parts[0]
        if int(month) > 12:
            raise ValueError("Invalid month")

        if int(day) > 31:
            raise ValueError("Invalid day")

        return value


class AfilioSalesCLI():
    def run(self, input_data):
        args = self.fetch(input_data)
        self.perform(args)

    def perform(self, args):
        credentials = json.load(args.credentials)

        api = AfilioSalesAPI(affiliate_id=credentials["affiliate_id"],
                             token=credentials["token"])

        program_id = args.programid if args.programid > 0 else None
        report = api.get_report(report_type=args.report_type,
                                date_start=args.date_start,
                                date_end=args.date_end,
                                program_id = program_id,
                                )

        json.dump(report, args.output)

    def fetch(self, input_data):
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("-t", "--type", dest="report_type", choices=["sale", "lead"], required=True)
        parser.add_argument("-p", "--program", dest="programid", type=int, help="Afilio Program ID", required=False, default=-1)
        parser.add_argument("-e", "--end", dest="date_end", type=DateFormat(), help="Format: YYYY-MM-DD", required=True)
        parser.add_argument("-s", "--start", dest="date_start", type=DateFormat(), help="Format: YYYY-MM-DD", required=True)
        parser.add_argument("-c", "--credentials", dest="credentials", type=argparse.FileType("r"), help='JSON file containing credentials token and Affiliate ID. format: {"token": <api_token>, "affiliate_id": <affiliate_id>}', required=True)
        parser.add_argument("-o", "--output", dest="output", type=argparse.FileType("w"), help='Output result file', default="-")

        return parser.parse_args(input_data)


if __name__ == "__main__":
    import sys
    AfilioSalesCLI().run(sys.argv[1:])


import unittest


class DateFormatTestCase(unittest.TestCase):
    def test_call_incomplete(self):
        self.assertRaise(ValueError, DateFormat().__call__, "2019-13-01")
        self.assertRaise(ValueError, DateFormat().__call__, "2019-11-32")

    def test_call_incomplete(self):
        self.assertRaises(ValueError, DateFormat().__call__, "")
        self.assertRaises(ValueError, DateFormat().__call__, "2019")
        self.assertRaises(ValueError, DateFormat().__call__, "2019-10")
        self.assertRaises(ValueError, DateFormat().__call__, "2019-10-1")

    def test_call_valid(self):
        self.assertEqual("2019-10-11", DateFormat()("2019-10-11"))


class AfilioSalesAPITestCase(unittest.TestCase):
    def test_invalid_params(self):
        self.assertRaises(ValueError, AfilioSalesAPI(None, None)._build_params, report_type=None, date_start=None, date_end=None)
        self.assertRaises(ValueError, AfilioSalesAPI(None, None)._build_params, report_type="a", date_start=None, date_end=None)

    def test_lead_request_params(self):
        api = AfilioSalesAPI("token", "affid")
        base_params = dict(affid=api.affiliate_id, token=api.token, format="json", mode="list")

        date_start = "2016-03-01"
        date_end = "2016-03-31"

        expected = {}
        expected.update(base_params)
        expected["type"] = AfilioSalesAPI.LEADS
        expected["dateStart"] = date_start
        expected["dateEnd"] = date_end
        self.assertCountEqual(expected,
                              api._build_params(report_type=AfilioSalesAPI.LEADS, date_start=date_start, date_end=date_end))
