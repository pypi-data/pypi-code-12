import ftplib
import datetime
import re

import pyxb.utils.domutils as domutils
from darwinpush import Source

import logging
log = logging.getLogger("ftp")

ftp_server = "datafeeds.nationalrail.co.uk"

# Downtime required to need logs from Darwin.
log_threshold = datetime.timedelta(minutes=5)

# Downtime required to need a snapshot.
snapshot_threshold = datetime.timedelta(days=1)

# A downtime <=0 downlods the snapshot and all the logs.


_snapshot_pattern = re.compile("^([0-9]{4})([0-9]{2})([0-9]{2}).*_v8\.xml\.gz$")
_log_pattern = re.compile(
    "^pPortData.log.([0-9]{4})-([0-9]{2})-([0-9]{2})-([0-9]{2})-([0-9]{2})$"
)

class LoginFail(Exception): pass


def fetchAll(client, downtime, server=ftp_server, user=None, passwd=None):
    """Download all the FTP files required, parse them and pass them to the
    client.

    It connects to the FTP server, downloads the required files and passes the
    messages to the client, and disconnects from the FTP server.

    This method blocks until it's done processing.

    Args:
        client: Must have a on_message(headers, message, source) method, which
              will be called for every valid message parsed.

        downtime: An int representing the number of seconds of downtime. It
                can also be a datetime.timedelta representing the downtime.

                If the number of seconds is:
                    <=0, then the snapshot for the day will be downloaded
                         and applied, and also all the logs.

                         NOT YET IMPLEMENTED.

                    >0,  all the required logs are downloaded. This means no
                         logs if less than 5 min (300 s) downtime, as Darwin
                         holds 5 minutes of messages in the queue before it
                         pushes the log to the FTP server and removes the
                         messages from the waiting queue.

                When the files from FTP are parsed, only the messages that
                are timestamped by darwin as being sent starting from
                `current_time - downtime` will be sent to the listener.

        server: FTP server to use. Default: "datafeeds.nationailrail.co.uk".
        user: FTP username, default None.
        passwd: FTP password, default None.
    """

    if type(downtime) is not datetime.timedelta:
        downtime = datetime.timedelta(seconds=downtime)

    #snapshot = downtime.total_seconds() <= 0 or downtime > snapshot_threshold
    logs = downtime.total_seconds() <= 0 or downtime > log_threshold

    #if not snapshot and not logs:
    if not logs:
        log.info("No work needed.")
        return

    with ftplib.FTP(server) as ftp:
        # Increase max line size. Darwin messages can be large.
        ftp.maxline = 819100
        login(ftp, user, passwd)

    #    if snapshot:
    #        get_snapshot(ftp, client)

        if logs:
            date = datetime.datetime.now() - downtime
            get_logs(ftp, client, date)


def login(ftp, user, passwd):
    res = ftp.login(user, passwd)

    r = res.split(" ")
    # be paranoic just in case weird things happened
    if len(r) < 1:
        raise LoginFail("Unexpected response message: %s", res)

    # response code
    resCode = int(r[0])
    if resCode == 230:
        # this is the
        return ftp

    raise LoginFail(res)

def get_logs(ftp, client, date):
    fnames = log_filenames(ftp, date)
    def callback(msg):
        return client.on_ftp_message(msg, source=Source.ftp_log)

    for f in fnames:
        # TODO filter out duplicate messages, if any
        file_callback(ftp, f, callback)

def get_snapshot(ftp, client):
    """Snapshots not supported yet."""
    pass


def file_callback(ftp, file, callback):
    """Get a FTP file line by line."""
    ftp.retrlines("RETR " + file, callback)

def file_to_memory(ftp, file):
    """Get a whole FTP file in memory as bytes."""
    bs = bytearray()
    ftp.retrbinary("RETR " + file, bs.extend)
    return bs

def _snapshot_filename_key(item):
    m = _snapshot_pattern.match(item)
    if not m:
        return ValueError("item is expected to be a snapshot filename")
    return datetime.date(
        year=int(m.group(1)),
        month=int(m.group(2)),
        day=int(m.group(3))
    )

def snapshot_filename(ftp):
    """Get the filename of the latest snapshot."""
    files = ftp.nlst()
    files = [i for i in filter(lambda x: _snapshot_pattern.match(x), files)]
    if len(files) == 0:
        log.warning("Could not file any snapshot file!")
        return None

    if len(files) == 1:
        return files[0]

    log.warning("Found many snapshot files. Returned the latest one.")
    mx = max(files, key=_snapshot_filename_key)
    return mx

def _log_filenames_filter(min_date):
    min5 = datetime.timedelta(minutes=5)

    def filter_func(item):
        m = _log_pattern.match(item)

        if not m:
            return None

        date = datetime.datetime(
            year = int(m.group(1)),
            month = int(m.group(2)),
            day = int(m.group(3)),
            hour = int(m.group(4)),
            minute = int(m.group(5))
        )

        # +min5 because the dates in the filename are the start_dates,
        # and we don't want to miss any message, in this case:
        #
        #                 min_date
        #           ---------|---------------------> time
        # blocks:     [   ][ x ][   ][   ][   ]
        #
        # So (date >= min_date) == False but we want that file, for the x block.

        return date + min5 >= min_date

    return filter_func


def log_filenames(ftp, min_date):
    """Get log filenames from ftp."""
    files = ftp.nlst()
    return filter(_log_filenames_filter(min_date), files)
