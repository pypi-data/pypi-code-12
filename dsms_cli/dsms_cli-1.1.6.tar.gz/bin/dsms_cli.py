#! /usr/bin/env python

"""
Usage:
    dsms_cli
    dsms_cli export [--ignore_ssl_errs] [--query=profile:phishing]
                    [--template=<s>] [--template_dir=mytemplates] [--redact]
    dsms_cli export [--ignore_ssl_errs] --list_templates
                    [--template_dir=/home/tom/mytemplates]
    dsms_cli list (profiles|severities|schedules) [--ignore_ssl_errs]
    dsms_cli add (location|file) --profile=<profile_id> --schedule=<schedule_id>
                 [--severity=<severity_id>] [--monitor_until=<monitor_until>]
                 [--tags=<tags>] [--ignore_ssl_errs] <location_or_file_path>

Options:
  export
    --ignore_ssl_errs        Ignore errors with SSL certs (e.g. self signed)
    --list_templates         List default templates available
    --query=<s>              DSMS search to run [default: age:7]
    --redact                 Remove sensitive URL info, e.g. embedded email
                             addresses, with REDACTED
    --template=<s>           Output format of report [default: standard]
    --template_dir=<s>       Path to a directory containing extra templates
  list
    profiles                 Show a list of all profiles available
    severities               Show a list of all severities available
    schedules                Show a list of all monitoring schedules available
  add
    location                 Specify you want to add a location (URL or domain)
    file                     Specify you want to upload a file
    --profile=<profile_id>   ID of profile to analyse with
    --schedule=<schedule_id> ID of schedule to run analysis
    --severity=<severity_id> ID of severity to process with
                             [default: 2]
    --monitor_until=<monitor_until>
                             yyyy-mm-dd cutoff date to cease monitoring
    --tags=<tags>            Comma separated tags to add, e.g. mytag, "tag 2"
    location_or_file_path    URL or domain to register, or file path to upload

Required environmental variables:
    * DSMS_SERVER (e.g. https://mydsmsserver)
    * DSMS_USER (e.g. tom)
    * DSMS_PASS (e.g. ThisIsMyPassword)
    * DSMS_SERVER_CERT (optional: e.g. /usr/share/ca-certificates/dsmserver.crt)

Examples:
  ##### Searching
  # Find all targets with domain or URL *.example.com
  dsms_cli export --query=*.example.com
  # Find a profile with a space in the name - note extra quotes!
  dsms_cli export --query="'Malware (file)'"

  ##### Getting IDs for registrations
  # Get ID numbers for various profiles, schedules and severities
  dsms_cli list profiles
  dsms_cli list schedules
  dsms_cli list severities

  ##### Adding targets
  # Note that "add location" matches targets with "Domain" and "URL" inputs,
  # and "add file" matches targets with "File path" inputs.
  #
  # Add a phishing URL with a regular schedule. IDs from
  # "dsms_cli list profiles" and "dsms_cli list schedules".
  dsms_cli add location --profile=1 --schedule=1 http://example.com
  # Add a domain for tracking. Look up your domain tracking profile, YMMV
  dsms_cli add location --profile=4 --schedule=1 example.com
  # Add malware for analysis
  dsms_cli add file --profile=3 --schedule=1 --tags=Troj.BAD sample.exe
"""

from __future__ import print_function
import sys
import dsms_cmd.dsms_cmd as dcmd

from docopt import docopt


def lister(args):
    r = dcmd.DSMSLister(ignore_ssl_errs=args.get("--ignore_ssl_errs"))
    output = "That's not something I can show."

    if args.get("schedules"):
        output = r.fetch_and_format("schedules")
    elif args.get("profiles"):
        output = r.fetch_and_format("profiles")
    elif args.get("severities"):
        output = r.fetch_and_format("severities")
    print(output, end="")

    sys.exit()


def add(args):
    target_type = dcmd.LOCATION_FLAG

    if args.get("file"):
        target_type = dcmd.FILE_FLAG

    r = dcmd.DSMSAdder(ignore_ssl_errs=args.get("--ignore_ssl_errs"))

    success = r.add(
        target_type, args.get("<location_or_file_path>"),
        schedule=args.get("--schedule"), profile=args.get("--profile"),
        severity=args.get("--severity"),
        monitor_until=args.get("--monitor_until"), tags=args.get("--tags"))

    sys.exit(0 if success else 1)


def list_templates(args):
    """
    Print a text list of template names available to be passed into the
    --template parameter.
    """
    r = dcmd.DSMSReporter(do_auth=False)
    print("\n".join(
        sorted(
            r.list_templates(template_dir=args.get("--template_dir"))
        )
    ))
    sys.exit()


def run_report(args):
    """
    Attempt to auth to DSMS, run a --query if provided or get everything,
    then try to render with --template in the default template path or a custom
    --template_dir.
    Print to stdout.
    """
    try:
        r = dcmd.DSMSReporter(ignore_ssl_errs=args.get("--ignore_ssl_errs"),
                              redact=args.get("--redact"))

        data = r.query_data(args.get("--query"))
        print(r.output(data, template=args.get("--template"),
                       template_dir=args.get("--template_dir")))
    except (RuntimeError, ValueError) as e:
        sys.exit(str(e))


def main():
    args = docopt(__doc__)

    if args.get("list"):
        lister(args)
    elif args.get("add"):
        add(args)
    elif args.get("export"):
        if args.get("--list_templates"):
            list_templates(args)
        else:
            run_report(args)
    else:
        print("Not a valid command.")
        print(__doc__)


if __name__ == "__main__":
    main()
