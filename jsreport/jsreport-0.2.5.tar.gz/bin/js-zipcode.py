#!/usr/bin/env python
"""
Helper script to pull data from https://www.justserve.org.
"""
from jsreport import get_project_count
# Main entry point, when run as a script
from datetime import datetime
import argparse

# Collect the command-line arguments
parser = argparse.ArgumentParser(
        description="Retrieve the number of JustServe projects at a zipcode.")
parser.add_argument("zipcode", 
        help="The five digit zipcode at the center of the search radius.")
parser.add_argument("-r", "--radius", default="5",
        choices=["5", "10", "15", "25", "50", "75"],
        help="The search radius, in miles. Defaults to 5.")
parser.add_argument("-d", "--driver", default="firefox",
        choices=["firefox", "chrome", "phantomjs"],
        help="The WebDriver to use. Defaults to firefox.")
parser.add_argument("-o", "--output", default="human",
        choices=["human", "csv", "json"],
        help="The output format. Defaults to human-readable.")
args = parser.parse_args()
# Go get the project count
project_count = get_project_count(args.zipcode, args.radius, args.driver)
# get today's date
now = datetime.now().strftime('%Y-%m-%d')
# Handle the output
if args.output=='csv':
    print "%s,%s,%s,%s" % (now, args.zipcode, args.radius, project_count)
elif args.output=='json':
    import json
    o = {'date': now, 'zipcode': args.zipcode, 'radius': args.radius,
            'project_count': project_count}
    print json.dumps(o)
else:
    print "%s projects within a %s mile radius of %s" % (project_count, 
            args.radius, args.zipcode)
