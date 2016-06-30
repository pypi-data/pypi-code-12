#    This file is part of KTBS <http://liris.cnrs.fr/sbt-dev/ktbs>
#    Copyright (C) 2011-2012 Pierre-Antoine Champin <pchampin@liris.cnrs.fr> /
#    Universite de Lyon <http://www.universite-lyon.fr>
#
#    KTBS is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    KTBS is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with KTBS.  If not, see <http://www.gnu.org/licenses/>.

"""
Implementation of the feed-import builtin methods.
"""
import traceback
from json import dumps as json_dumps, loads as json_loads
import logging
from time import mktime
from urllib import quote_plus

from rdflib import Literal, RDF, Namespace, URIRef

from rdfrest.util.iso8601 import ParseError
from rdfrest.util import Diagnosis, make_fresh_uri
from ktbs.methods.interface import IMethod
from ktbs.engine.builtin_method import register_builtin_method_impl
from ktbs.engine.resource import METADATA
from ktbs.namespace import KTBS

import feedparser

# pylint is confused by a module named time (as built-in module)

LOG = logging.getLogger(__name__)

NS = Namespace("http://tbs-platform.org/2015/feed-import#")

class _FeedImportMethod(IMethod):
    """I implement the feed-import builtin method.
    """
    uri = URIRef("http://champin.net/tmp/feed-import2")

    def compute_trace_description(self, computed_trace):
        """I implement :meth:`.interface.IMethod.compute_trace_description`.
        """
        diag = Diagnosis("feed-import.compute_trace_description")
        cstate = {
            "method": "feed-import",
            "feed": None,
            "etag": None,
            "lastseen": None,
        }

        params =  self._prepare_params(computed_trace, diag)

        if diag:
            assert params is not None
            model = NS[""]
            origin = Literal("1970-01-01T00:00:00Z")
            with computed_trace.edit(_trust=True) as editable:
                editable.add((computed_trace.uri, KTBS.hasModel, model))
                editable.add((computed_trace.uri, KTBS.hasOrigin, origin))

            cstate["feed"] = params.get("feed")

        else:
            cstate["errors"] = list(diag)


        computed_trace.metadata.set((
            computed_trace.uri,
            METADATA.computation_state,
            Literal(json_dumps(cstate))
        ))
        return diag

    def compute_obsels(self, computed_trace, from_scratch=False):
        """I implement :meth:`.interface.IMethod.compute_obsels`.
        """
        diag = Diagnosis("feed-import.compute_obsels")
        cstate = json_loads(
            computed_trace.metadata.value(computed_trace.uri,
                                          METADATA.computation_state, default="{}"))
        if from_scratch:
            cstate["etag"] = None
            cstate["lastseen"] = None

        errors = cstate.get("errors")
        if errors:
            for i in errors:
                diag.append(i)
                return diag

        target_obsels = computed_trace.obsel_collection
        feed = cstate.get("feed")
        etag = cstate.get("etag")
        lastseen = cstate.get("lastseen")

        resp = feedparser.parse(feed, etag=etag)
        if resp.status == 304:
            return diag
        if resp.status != 200:
            diag.append("Could not load feed: " + resp.debug_message)
            return diag

        # TODO built trace incrementally as much as possible
        target_obsels._empty() # friend #pylint: disable=W0212

        target_uri = computed_trace.uri
        with target_obsels.edit(_trust=True) as editable:
            target_add = editable.add
            namespaces = resp.namespaces
            subject = Literal(resp.feed.get("id") or resp.feed.get("title"))
            

            for entry in resp.entries:
                # TODO check that entry is not already there
                new_obs_uri = make_fresh_uri(editable,
                                             target_uri +
                                             quote_plus(entry.get("id", "e")))
                LOG.debug("--- generating %s", new_obs_uri)
                target_add((new_obs_uri, KTBS.hasTrace, target_uri))
                target_add((new_obs_uri, RDF.type, NS.entry))
                timestamp = int(mktime(entry.get("updated_parsed") or
                                       entry.get("published_parsed")))
                target_add((new_obs_uri, KTBS.hasBegin, Literal(timestamp)))
                target_add((new_obs_uri, KTBS.hasEnd, Literal(timestamp)))
                begindt = entry.get("updated") or entry.get("published")
                target_add((new_obs_uri, KTBS.hasBeginDT, Literal(begindt)))
                target_add((new_obs_uri, KTBS.hasEndDT, Literal(Literal(entry.updated))))
                target_add((new_obs_uri, KTBS.hasSubject, subject))

                for key, val in entry.items():
                    if _skip_key_val(key, val):
                        continue
                    if isinstance(val, list):
                        LOG.debug("skipping value list for %s", key)
                        continue
                    if isinstance(val, dict):
                        for key2, val2 in val.items():
                            if _skip_key_val(key2, val2):
                                continue
                            target_add((new_obs_uri,
                                        _prepare_predicate(key2, namespaces, key),
                                        _prepare_object(val2, key2)))
                    else:
                        target_add((new_obs_uri,
                                    _prepare_predicate(key, namespaces),
                                    _prepare_object(val, key)))

        cstate["etag"] = getattr(resp, "etag", None)
        cstate["lastseen"] = lastseen

        computed_trace.metadata.set((
            computed_trace.uri,
            METADATA.computation_state,
            Literal(json_dumps(cstate))
        ))
        return diag

    @staticmethod
    def _prepare_params(computed_trace, diag):
        """I check and prepare the data required by the method.

        I return the unique source of the computed trace, and a dict of
        useful parameters converted to the expected datatype. If this can not
        be done, I return ``(None, None)``.

        I also populate `diag` with error/warning messages.
        """
        sources = computed_trace.source_traces
        params = computed_trace.parameters_as_dict
        critical = False

        if len(sources) > 0:
            diag.append("Method FeedImport expects no source")
            critical = True

        for key, val in params.items():
            datatype = _PARAMETERS_TYPE.get(key)
            if datatype is None:
                diag.append("WARN: Parameter %s is not used by :feed-import"
                            % key)
            else:
                try:
                    params[key] = datatype(val)
                except ValueError:
                    LOG.info(traceback.format_exc())

                    diag.append("Parameter %s has illegal value: %s"
                                % (key, val))
                    critical = True
                except ParseError:
                    LOG.info(traceback.format_exc())
                    diag.append("Parameter %s has illegal value: %s"
                                % (key, val))
                    critical = True

        if "feed" not in params:
            diag.append("Parameter 'feed' is required")
            critical = True

        if critical:
            return None, None
        else:
            return params

def _skip_key_val(key, val):
    return (
        key.endswith("_parsed") or
        val is None or
        False)

def _prepare_predicate(key, namespaces, prekey=None):
    parts = key.split("_", 1)
    if len(parts) == 1 or parts[1] in { "detail", "parsed" }:
        if prekey:
            return NS['{}.{}'.format(prekey.split("_", 1)[0], key)]
        else:
            return NS[key]
    else:
        return URIRef(namespaces[parts[0]] + parts[1])

def _prepare_object(val, key):
    if key == "href" or key == "link":
        return URIRef(val)
    else:
        return Literal(val)


_PARAMETERS_TYPE = {
    "feed": URIRef,
}



def start_plugin(_config):
    """I get the configuration values from the main kTBS configuration.

    .. note:: This function is called automatically by the kTBS.
              It is called once when the kTBS starts, not at each request.
    """
    register_builtin_method_impl(_FeedImportMethod())

if __name__ == "__main__":
    print _FeedImportMethod()
