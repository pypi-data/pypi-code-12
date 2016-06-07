import logging

from future.backports.urllib.parse import parse_qs
from future.backports.urllib.parse import splitquery
from future.backports.urllib.parse import unquote
from future.backports.urllib.parse import urlparse
from oic.exception import ParameterError
from oic.exception import RedirectURIError
from oic.exception import UnknownClient
from oic.exception import URIError

logger = logging.getLogger(__name__)


class CDB(object):
    def __init__(self):
        self._db = {}

    def verify_redirect_uri(self, areq):
        """
        MUST NOT contain a fragment
        MAY contain query component

        :return: An error response if the redirect URI is faulty otherwise
            None
        """
        try:
            _redirect_uri = unquote(areq["redirect_uri"])

            part = urlparse(_redirect_uri)
            if part.fragment:
                raise URIError("Contains fragment")

            (_base, _query) = splitquery(_redirect_uri)
            if _query:
                _query = parse_qs(_query)

            match = False
            for regbase, rquery in self._db[str(areq["client_id"])][
                "redirect_uris"]:
                if _base == regbase or _redirect_uri.startswith(regbase):
                    # every registered query component must exist in the
                    # redirect_uri
                    if rquery:
                        for key, vals in rquery.items():
                            assert key in _query
                            for val in vals:
                                assert val in _query[key]
                    # and vice versa, every query component in the redirect_uri
                    # must be registered
                    if _query:
                        if rquery is None:
                            raise ValueError
                        for key, vals in _query.items():
                            assert key in rquery
                            for val in vals:
                                assert val in rquery[key]
                    match = True
                    break
            if not match:
                raise RedirectURIError("Doesn't match any registered uris")
            # ignore query components that are not registered
            return None
        except Exception as err:
            logger.error("Faulty redirect_uri: %s" % areq["redirect_uri"])
            try:
                _cinfo = self._db[str(areq["client_id"])]
            except KeyError:
                try:
                    cid = areq["client_id"]
                except KeyError:
                    logger.error('No client id found')
                    raise UnknownClient('No client_id provided')
                else:
                    logger.info("Unknown client: %s" % cid)
                    raise UnknownClient(areq["client_id"])
            else:
                logger.info("Registered redirect_uris: %s" % _cinfo)
                raise RedirectURIError(
                    "Faulty redirect_uri: %s" % areq["redirect_uri"])

    def get_redirect_uri(self, areq):
        """ verify that the redirect URI is reasonable

        :param areq: The Authorization request
        :return: Tuple of (redirect_uri, Response instance)
            Response instance is not None of matching redirect_uri failed
        """
        if 'redirect_uri' in areq:
            self.verify_redirect_uri(areq)
            uri = areq["redirect_uri"]
        else:
            raise ParameterError(
                "Missing redirect_uri and more than one or none registered")

        return uri

    def __setitem__(self, key, value):
        self._db[key] = value

    def __getitem__(self, item):
        return self._db[item]

    def __len__(self):
        return len(self._db)

    def items(self):
        return self._db.items()

    def keys(self):
        return self.keys()

    def values(self):
        return self.values()
