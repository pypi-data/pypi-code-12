import os
import requests
from requests.packages.urllib3.exceptions import (
    InsecureRequestWarning, SubjectAltNameWarning)
import logging
import jinja2 as j2
import iso8601
import copy


logger = logging.getLogger(name=__name__)
logging.basicConfig(level=logging.WARN)

isodatelog = logging.getLogger("iso8601.iso8601")
isodatelog.setLevel(logging.WARN)

URL_TOKEN = "/token/new.json"
URL_SEARCH = "/api/v1/target/search/"
URL_SHOW_PROFILES = "/api/v1/profile/all/"
URL_SHOW_SCHEDULES = "/api/v1/schedule/all/"
URL_SHOW_SEVERITIES = "/api/v1/severity/all/"
URL_CREATE_TARGET = "/api/v1/target/create/"

MAX_FETCHES = 1000

LOCATION_FLAG = 1
FILE_FLAG = 2


def _get_setting(key, fail_on_missing=True):
    val = os.environ.get(key, None)

    if fail_on_missing and not val:
        raise ValueError("Missing {} from environment settings".format(key))
    elif not val:
        return
    return val


def _str_to_datetime(date_iso8601_str):
    try:
        return iso8601.parse_date(date_iso8601_str)
    except:
        return None


def _format_dsms_error(err_data):
    out = ""

    for field, data in err_data.get("errors").items():
        if field == "__all__":
            field = "Overall"
        out += "    {0}: {1}\n".format(field, ", ".join(data))

    return out


class DSMSClientObject(object):
    """
    Provides functions to an object to allow it to create a authenticated
    session with a DSMS server.

    ignore_ssl_errs: set True to ignore any SSL certificate errors (e.g. self
                     signed certs)
    do_auth:         default: True. Set False to avoid authenticating to a
                     DSMS server (speeds up certain operations)
    """

    def __init__(self, ignore_ssl_errs=False, do_auth=True):
        self.server = _get_setting("DSMS_SERVER")
        self.username = _get_setting("DSMS_USER")
        self.password = _get_setting("DSMS_PASS")
        self.user_id = None
        self.token = None
        self.ignore_ssl_errs = ignore_ssl_errs
        self.do_auth = do_auth

        if do_auth:
            self._create_session()

    @property
    def _request_params(self):
        params = {}

        if self.ignore_ssl_errs:
            params["verify"] = not self.ignore_ssl_errs
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        else:
            try:
                cert_path = _get_setting("DSMS_SERVER_CERT")
                with open(cert_path):
                    params["verify"] = cert_path
                    requests.packages.urllib3.disable_warnings(
                        SubjectAltNameWarning)
            except ValueError:  # DSMS_SERVER_CERT env var not set
                pass
            except IOError:  # cert does not exist
                raise RuntimeError(
                    "Couldn't find valid server cert at {}".format(cert_path))
        return params

    def _create_session(self):
        """
        Authenticate to a DSMS server, get a token and user_id
        """
        params = {'username': self.username, 'password': self.password}

        try:
            resp = requests.post("{0}{1}".format(self.server, URL_TOKEN),
                                 data=params, **self._request_params)
            jresp = resp.json()

            if jresp.get("success"):
                self.token = jresp["token"]
                self.user_id = jresp["user"]
                logger.debug("Created session")
            else:
                raise RuntimeError("DSMS login failed")
        except (requests.ConnectionError, requests.RequestException) as e:
            raise RuntimeError("Error during login: {}".format(str(e)))
        except KeyError:
            raise RuntimeError("Couldn't get username or token from response")


class DSMSReporter(DSMSClientObject):
    """
    DSMSReporter authenticates to a DSMS server, run a query, then transforms
    and outputs those results based on a Jinja2 template.

    """
    def __init__(self, *args, **kwargs):
        self.redact = kwargs.pop("redact", False)

        super(DSMSReporter, self).__init__(*args, **kwargs)

    def fetch_page(self, search, page):
        """
        Run a single query to the DSMS web API and return the JSON results.
        Raises RuntimeError if we hit any problems, e.g. server down or results
        aren't JSON.
        """
        get_params = {
            'target_filter': search,
            'page': page,
        }
        post_data = {
            'user': self.user_id,
            'token': self.token,
        }

        if self.redact:
            get_params["redact"] = "1"

        try:
            resp = requests.post("{0}{1}".format(self.server, URL_SEARCH),
                                 params=get_params,
                                 data=post_data,
                                 **self._request_params)
            return resp.json()
        except (requests.ConnectionError, requests.RequestException) as e:
            raise RuntimeError("Couldn't establish session with DSMS: {}"
                               .format(e))
        except ValueError as e:  # JSON parse error
            raise RuntimeError("Error during data fetch: {}".format(e))

    def query_data(self, search):
        """
        Based on a DSMS search query, search, ask DSMS for matching records.
        Loops over each page of results returned by the DSMS API, and returns
        a concatenated list of dicts containing all results.

        Limited to fetching result pages MAX_FETCHES times.
        """
        logger.debug("Searching for {}".format(search))
        page = None
        next_page_num = 1
        last_page_num = 0
        fetch = True
        fetch_count = 0

        results = []

        while fetch:
            if last_page_num == next_page_num:
                raise RuntimeError("We've fetched the same page of results "
                                   "twice: something has gone wrong.")

            page = self.fetch_page(search, next_page_num)

            for result in page.get("results", []):
                result["added"] = _str_to_datetime(result.get("added", ""))
                results.append(result)

            last_page_num = next_page_num
            if page.get("next_page"):
                next_page_num = page.get("next_page")
            else:
                fetch = False

            fetch_count += 1

            if fetch_count > MAX_FETCHES:
                logger.warn("Exceeded maximum number of API fetches at {}, "
                            "truncating results".format(MAX_FETCHES))
                fetch = False

        return results

    def list_templates(self, template_dir=None):
        """
        Return a list of templates found in the default and any custom template
        directories. Strips the '.j2' path from the end, to present in format
        ready for inclusion in --template argument.
        """
        loader = self._get_template_loader(
            template_dir=template_dir)
        jenv = j2.Environment(loader=loader)
        return [f.replace(".j2", "") for f in jenv.list_templates()]

    def _get_template_loader(self, template_dir=None):
        """
        Returns a jinja2 template loader with the default template path and
        a custom template path if one has been supplied.

        This is passed into a jinja2 Environment later on for template
        discovery.
        """
        template_paths = [os.path.join(os.path.dirname(__file__), "templates")]

        if template_dir:
            template_paths.append(template_dir)

        return j2.FileSystemLoader(template_paths)

    def output(self, data, template="standard", template_dir=None):
        """
        Given a list of dicts containing DSMS records, pass this to a template
        supplied by the template parameter. Return the rendered result.

        data: list of dicts to be passed to template
        template: name of jinja2 template to use with extension removed
        template_dir: optional search path for templates.
        """
        loader = self._get_template_loader(
            template_dir=template_dir)
        jenv = j2.Environment(loader=loader)

        try:
            template_file = "{}.j2".format(template)
            logger.debug("Using template file {}".format(template_file))
            template = jenv.get_template(template_file)
            return template.render(records=data)
        except IOError as e:
            raise RuntimeError("Couldn't open template file {0}: {1}"
                               .format(template, e))
        return data


class DSMSLister(DSMSClientObject):
    """
    Produces simple text lists displaying results of DSMS APIs.
    """
    _types = {
        "profiles": {
            "url": URL_SHOW_PROFILES,
            "title": "{0: <40}{1: <15}{2}".format("Profile", "Input", "ID"),
            "format": "{name: <40}{input_type: <15}{id}",
            "sort": "name",
        },
        "schedules": {
            "url": URL_SHOW_SCHEDULES,
            "title": "{0: <40}{1}".format("Schedule name", "ID"),
            "format": "{name: <40}{id}",
            "sort": "name",
        },
        "severities": {
            "url": URL_SHOW_SEVERITIES,
            "title": "{0: <20}{1}".format("Severity", "ID"),
            "format": "{name: <20}{id}",
            "sort": "name",
        },
    }

    def __init__(self, *args, **kwargs):
        super(DSMSLister, self).__init__(*args, **kwargs)

    def fetch_and_format(self, show_type):
        data = self.fetch_data(show_type)
        return self.format_output(show_type, data)

    def fetch_data(self, show_type):
        post_data = {
            'user': self.user_id,
            'token': self.token,
        }

        try:
            resp = requests.post(
                "{0}{1}".format(self.server, self._types[show_type]["url"]),
                data=post_data, **self._request_params)
        except KeyError:
            raise RuntimeError("Can't show {}. Should be one of: {}".format(
                show_type, ", ".join(self._types.keys())))
        except (requests.ConnectionError, requests.RequestException) as e:
            raise RuntimeError("Couldn't establish session with DSMS: {}"
                               .format(e))
        return resp.json()["results"]

    def format_output(self, show_type, json_out):
        out = ""

        def _get_sort_field(a):
            return a.get(self._types[show_type]["sort"])

        out += self._types[show_type]["title"] + "\n"
        out += "-" * len(self._types[show_type]["title"]) + "\n"

        for data in sorted(json_out, key=_get_sort_field):
            out += self._types[show_type]["format"].format(**data) + "\n"

        return out


class DSMSAdder(DSMSClientObject):
    def __init__(self, *args, **kwargs):
        super(DSMSAdder, self).__init__(*args, **kwargs)

        lister = DSMSLister(ignore_ssl_errs=kwargs.get("ignore_ssl_errs"))
        self.profiles = lister.fetch_data("profiles")
        self.schedules = lister.fetch_data("schedules")
        self.severities = lister.fetch_data("severities")

    def add(self, target_type, location_or_file_path, schedule=None,
            profile=None, severity=None, monitor_until=None, tags=None):
        location = None
        file_path = None
        req_args = copy.copy(self._request_params)

        if target_type == LOCATION_FLAG:
            location = location_or_file_path
        elif target_type == FILE_FLAG:
            file_path = location_or_file_path
            if os.path.exists(file_path):
                req_args["files"] = [
                    ("artifact_file", ("sample", open(file_path, "rb"), 'data'))
                ]
            else:
                print("Couldn't find file {}".format(file_path))
                return False

        post_data = {
            'user': self.user_id,
            'token': self.token,
            'location': location,
            'schedule': schedule,
            'profile': profile,
            'severity': severity,
            'monitor_until': monitor_until,
            'tags': tags,
        }

        try:
            resp = requests.post(
                "{0}{1}".format(self.server, URL_CREATE_TARGET),
                data=post_data, **req_args)
        except (requests.ConnectionError, requests.RequestException) as e:
            raise RuntimeError("Couldn't establish session with DSMS: {}"
                               .format(e))

        result = resp.json()
        success = result.get("success")

        if not success:
            print("DSMS had some problems registering your target:")
            print(_format_dsms_error(resp.json()))
        else:
            print "Target {} added.".format(result.get("id"))

        return success
