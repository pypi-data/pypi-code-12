""" Plugin to parse helga logs from CHANNEL_LOGGING_DIR """
import optparse
import os
import re
import requests
import traceback

from datetime import date, datetime
from helga import settings
from helga.plugins import command

_help_text = 'Show log for dates, nicks, and terms e.g. !log --start_date 2015-01-02'


@command('log', help=_help_text)
def log_reader(client, channel, nick, message, cmd, args):
    """ Show logs for dates  or terms """
    options, logs = parse_logs(args, channel)
    return post_dpaste(logs, options.channel + ' logs')


def post_dpaste(content, title):
    """ Post content to dpaste """
    if not content:
        return 'No content to paste!'
    payload = {'title': title, 'content': content}
    response = requests.post('http://dpaste.com/api/v2/', payload)
    location = response.headers.get('location', '')
    if response.status_code == 201 or location:
        if not location:
            return 'dpaste location empty, probably no contents?'
        return location
    if response.status_code == 413:
        return "Response too big for dpaste, please narrow your query"
    return 'dpaste.com rejected log post with status: ' + str(response.status_code)


def parse_logs(args, channel):
    """ Parse all logs matching args """
    options, _ = parse_args(args, channel)
    start_date = parse_date(options.start_date)
    end_date = parse_date(options.end_date)
    start_time = parse_time(options.start_time)
    end_time = parse_time(options.end_time)
    results = []
    log_dir = os.path.join(settings.CHANNEL_LOGGING_DIR, options.channel)
    for f in os.listdir(log_dir):
        try:
            file_date = parse_date(f[:-4])
            if file_date >= start_date and file_date <= end_date:
                middle_date = file_date > start_date and file_date < end_date
                parse_file(results, log_dir, f, middle_date, start_time,
                           end_time, options.nick, options.text)
        except:
            traceback.print_exc()
    return options, ''.join(results)


def parse_file(results, log_dir, file_name, middle_date, start_time, end_time, nick, text):
    """ Grab results from file """
    file_path = os.path.join(log_dir, file_name)
    with open(file_path, 'r') as f:
        # need to verify lines that dont start with date are still valid logworthy lines
        valid = False
        for line in f:
            try:
                time = parse_time(line[:8])
                nick_matches = re.match(nick, line.split('-')[1].strip())
                time_matches = middle_date or (time >= start_time and time <= end_time)
                text_matches = re.search(text, line.split('-')[2])
                valid = nick_matches and time_matches and text_matches
            except ValueError:
                # not a line with date at the beginning, use last validity check
                pass
            if valid:
                results.append(line)


def parse_date(date_string):
    """ Parse date from string """
    return datetime.strptime(date_string, '%Y-%m-%d')


def parse_time(time_string):
    """ Parse time from string """
    return datetime.strptime(time_string, '%H:%M:%S')


def parse_args(args, channel=''):
    """ Create option parser and parse """
    parser = optparse.OptionParser()
    parser.add_option('-s', '--start_date', default=str(date.today()))
    parser.add_option('-e', '--end_date', default=str(date.today()))
    parser.add_option('-d', '--start_time', default='00:00:00')
    parser.add_option('-r', '--end_time', default='23:59:59')
    parser.add_option('-c', '--channel', default=channel)
    parser.add_option('-n', '--nick', default='.*')
    parser.add_option('-t', '--text', default='.*')
    return parser.parse_args(args)
