# coding: utf-8
import json
import mimetypes
from os.path import basename
import requests


CLOUDPRINT_URL = 'https://www.google.com/cloudprint'


def get_job(job_id, printer=None, **kwargs):
    """
    Returns the data for a single job.

    :param      job_id: print job ID
    :type       job_id: string
    :param printer: if known, the printer id
    :type  printer: string
    :returns: `dict` expressing a job, or `None`

    This is a convience method that uses `list_jobs`, as there is no "get job"
    API for Google Cloud Print.
    """
    jobs = list_jobs(printer=printer, **kwargs)
    for job in jobs:
        if job['id'] == job_id:
            return job


def delete_job(job_id, **kwargs):
    """
    Delete a print job.

    :param job_id: job ID
    :type  job_id: string

    :returns: API response data as `dict`, or the HTTP response on failure
    """
    url = CLOUDPRINT_URL + '/deletejob'
    r = requests.post(url, data={'jobid': job_id}, **kwargs)
    if r.status_code == requests.codes.ok:
        return r.json()
    else:
        raise requests.RequestException(r.text)


def list_jobs(printer=None, **kwargs):
    """
    List print jobs.

    :param printer: filter by a printer id
    :type  printer: string

    :returns: API response data as `dict`, or the HTTP response on failure

    Jobs are represented as `list` of `dict`::

        >>> list_jobs(auth=...)['jobs']
        [...]

    """
    params = {}
    if printer is not None:
        params['printerid'] = printer
    url = CLOUDPRINT_URL + '/jobs'
    r = requests.get(url, params=params, **kwargs)

    if r.status_code == requests.codes.ok:
        # At the time of writing, the `/jobs` API returns `Content-Type:
        # text/plain` header
        return (r.json() if hasattr(r, 'json') else json.loads(r.text))['jobs']
    else:
        raise requests.RequestException(r.text)


def list_printers(**kwargs):
    """
    List registered printers.

    :returns: API response data as `dict`

    Printers are represented as `list` of `dict`.

        >>> list_printers(auth=...)['printers']
        [...]

    """
    url = CLOUDPRINT_URL + '/search'
    r = requests.get(url, **kwargs)
    if r.status_code == requests.codes.ok:
        return r.json()
    else:
        raise requests.RequestException(r.text)


def get_printer(printer_id, **kwargs):
    """
    Gets a specific printer.

    :returns: API response data as `dict`.

    Printers are represented as `list` of `dict`
    """
    url = CLOUDPRINT_URL + '/printer'
    r = requests.get(url, params={'printerid': printer_id}, **kwargs)
    if r.status_code == requests.codes.ok:
        printers = r.json()['printers']
        if len(printers) == 1:
            return printers[0]
        else:
            raise Exception('Unexpected response from Google Cloud print.')
    else:
        raise requests.RequestException(r.text)


def submit_job(printer, content=None, content_bytes=None, title=None, capabilities=None, tags=None, content_type=None, **kwargs):
    """
    Submit a print job.

    :param       printer: the id of the printer to use
    :type        printer: string
    :param       content: what should be printer
    :type        content: ``(name, file-like)`` pair or path
    :param       content_bytes: raw file to print
    :type        content_bytes: bytearray
    :param  capabilities: capabilities for the printer
    :type   capabilities: list
    :param         title: title of the print job, should be unique to printer
    :type          title: string
    :param          tags: job tags
    :type           tags: list
    :params content_type: explicit mimetype for content
    :type   content_type: string

    :returns: API response data as `dict`, or the HTTP response on failure

    The newly created job is represented as a `dict` in ``job``::

        >>> submit_job(...)['job']
        {...}

    See https://developers.google.com/cloud-print/docs/appInterfaces#submit for
    details.
    """
    # normalise *content* to bytes, and *name* to a string
    if content is not None:
        if isinstance(content, (list, tuple)):
            name = content[0]
            content = content[1].read()
        else:
            name = basename(content)
            with open(content, 'rb') as f:
                content = f.read()

        if title is None:
            title = name
    else:
        name = title
        content = content_bytes

    if capabilities is None:
        # magic default value
        capabilities = [{}]

    files = {'content': (name, content)}
    data = {
        'printerid': printer,
        'title': title,
        'contentType': content_type or mimetypes.guess_type(name)[0],
        'capabilities': json.dumps({
            'capabilities': capabilities
        })
    }

    if tags:
        data['tag'] = tags

    url = CLOUDPRINT_URL + '/submit'
    r = requests.post(url, data=data, files=files, **kwargs)

    if r.status_code == requests.codes.ok:
        return r.json()
    else:
        raise requests.RequestException(r.text)
