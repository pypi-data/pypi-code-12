import base64
import gzip
import json
import os
import uuid
import datetime
import time
import StringIO


def nowms():
    """
    Returns the current moment as a number of milliseconds since epoch

    :rtype: int
    :return: Number of milliseconds since the epoch
    """
    nowdto = datetime.datetime.now()
    millis = time.mktime(nowdto.timetuple()) * 1000 + nowdto.microsecond / 1000
    return int(millis)


def wrap_string(s, gz=False, topicname="unassigned"):
    """
    Wraps a JSON string into a Trinity-like header and returns the wrapped
    string

    :type s: str
    :param s: Raw data to be input to Trinity

    :type gz: bool
    :param gz: If true, the input string is zipped and encoded base 64

    :rtype: str
    :return: Input string wrapped into Trinity-like header
    """
    event_header = {"version": "1.0",
                    "app_id": None,
                    "app_name": None,
                    "event_id": str(uuid.uuid4()),
                    "event_timestamp": None,
                    "server_timestamp": nowms(),
                    "accept_language": "en-us",
                    "server_ip_address": "10.129.66.253",
                    "topic_name": topicname,
                    "client_ip_address": "172.28.212.65"}

    trinitydict = {"event_header": event_header}

    if not gz:
        payload = s
    else:
        out = StringIO.StringIO()
        with gzip.GzipFile(fileobj=out, mode="w") as f:
            f.write(s)
        payload = base64.encodestring(out.getvalue())

    trinitydict.update({"payload": payload})
    return json.dumps(trinitydict)


def trinitify(input_file, topicname="unassigned"):
    """
    Wraps each JSON in the 'input_file' into a Trinity header and writes
    the resulting output to a file.

    :type input_file: str
    :param input_file: input file with raw data

    :type topicname: str
    :param topicname: Name of the trinity topic, if known by the user

    :rtype: None
    :return: None
    """
    input_file_name = os.path.basename(input_file)
    input_file_dir = os.path.dirname(input_file)

    name, extn = input_file_name.rsplit(".", maxsplit=1)

    output_file_name = "%s_trinitified.%s" % (name, extn)
    output_file = os.path.join(input_file_dir, output_file_name)

    with open(input_file, "r") as infile, open(output_file, "w") as outfile:
        for line in infile:
            wrapped_line = wrap_string(line, topicname=topicname)
            outfile.write("%s\n" % wrapped_line)
