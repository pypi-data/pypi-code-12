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
Implementation of the sequence builtin methods.
"""
import traceback
from json import dumps as json_dumps, loads as json_loads
import logging

from rdflib import Literal, RDF, URIRef

from rdfrest.util.iso8601 import ParseError
from rdfrest.util import Diagnosis
from ktbs.methods.interface import IMethod
from ktbs.methods.utils import translate_node
from ktbs.engine.builtin_method import register_builtin_method_impl
from ktbs.engine.resource import METADATA
from ktbs.namespace import KTBS

# pylint is confused by a module named time (as built-in module)

LOG = logging.getLogger(__name__)

# TODO very naive (greedy) implementation for the moment

class _SequenceMethod(IMethod):
    """I implement the sequence builtin method.
    """
    uri = URIRef("http://champin.net/tmp/sequence")

    def compute_trace_description(self, computed_trace):
        """I implement :meth:`.interface.IMethod.compute_trace_description`.
        """
        diag = Diagnosis("sequence.compute_trace_description")
        cstate = { "method": "sequence",
                   "target_otype": None,
                   "components": None,
                   "max_duration": None,
                   "max_noise": None,
                   "last_seen": None,
                   "str_mon_tag": None,
                   "current_source_obsels": [],
                   "current_begin": None,
                   "current_noise": 0,
        }

        src, params =  self._prepare_source_and_params(computed_trace, diag)
        if src is not None:
            assert params is not None
            model = params.get("model")
            if model is None:
                model = src.model_uri
            else:
                model = URIRef(model)
            origin = Literal(params.get("origin")  or  src.origin)
            with computed_trace.edit(_trust=True) as editable:
                editable.add((computed_trace.uri, KTBS.hasModel, model))
                editable.add((computed_trace.uri, KTBS.hasOrigin, origin))

            cstate["target_otype"] = params.get("target_otype")
            cstate["components"] = params.get("components")
            cstate["max_duration"] = params.get("max_duration")
            cstate["max_noise"] = params.get("max_noise")

        if not diag:
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
        diag = Diagnosis("sequence.compute_obsels")
        cstate = json_loads(
            computed_trace.metadata.value(computed_trace.uri,
                                          METADATA.computation_state))
        if from_scratch:
            cstate["str_mon_tag"] = None

        errors = cstate.get("errors")
        if errors:
            for i in errors:
                diag.append(i)
                return diag

        source = computed_trace.source_traces[0]
        source_obsels = source.obsel_collection
        target_obsels = computed_trace.obsel_collection
        target_otype = URIRef(cstate["target_otype"])
        components = _prepare_components(cstate["components"])
        max_duration = cstate.get("max_duration", None)
        max_noise = cstate.get("max_noise", None)
        old_str_mon_tag = cstate["str_mon_tag"]
        last_seen = cstate["last_seen"]
        current_source_obsels = [ URIRef(i)
                                  for i in cstate["current_source_obsels"] ]
        current_begin = cstate["current_begin"]
        current_noise = cstate["current_noise"]

        begin = None
        if old_str_mon_tag == source_obsels.str_mon_tag:
            # stritcly temporally monotonic change; start at last_seen
            LOG.debug("strictly temporally monotonic %s", computed_trace)
            if last_seen:
                begin = last_seen
        else:
            # non-temporally monotonic (or non monotonic) change;
            # empty the graph and start anew
            LOG.debug("not temporally monotonic %s", computed_trace)
            target_obsels._empty() # friend #pylint: disable=W0212
            last_seen = None
            current_source_obsels = []
            current_begin = None
            current_noise = 0

        source_uri = source.uri
        target_uri = computed_trace.uri
        source_state = source_obsels.state
        source_triples = source_state.triples
        with target_obsels.edit(_trust=True) as editable:
            target_add = editable.add

            for obs in source.iter_obsels(begin=begin, refresh="no"):
                last_seen = obs.begin

                obs_uri = obs.uri
                obs_state = obs.state
                tests = components[len(current_source_obsels)]
                reset = False
                match = True
                if (current_begin is not None and
                    max_duration is not None and
                    obs.end - current_begin > max_duration):

                    LOG.debug("--- max_duration reached by %s", obs)
                    reset = True
                    match = False

                else:
                    for test in tests:
                        if (obs_uri, test[0], test[1]) not in obs_state:
                            match = False
                            break
                            
                if match:
                    LOG.debug("--- matching %s", obs)
                    current_source_obsels.append(obs_uri)
                    if len(current_source_obsels) == 1:
                        current_begin = obs.begin;
                    if len(current_source_obsels) == len(components):
                        new_obs_uri = translate_node(obs.uri, computed_trace,
                                                     source_uri, False)
                        LOG.debug("--- generating %s", new_obs_uri)
                        target_add((new_obs_uri, KTBS.hasTrace, target_uri))
                        target_add((new_obs_uri, RDF.type, target_otype))
                        target_add((new_obs_uri, KTBS.hasSubject,
                                    Literal(obs.subject)))
                        for i in current_source_obsels:
                            target_add((new_obs_uri, KTBS.hasSourceObsel, i))
                        target_add((new_obs_uri, KTBS.hasBegin,
                                    Literal(current_begin)))
                        target_add((new_obs_uri, KTBS.hasEnd,
                                    Literal(obs.end)))
                        reset = True
                        
                else:
                    if len(current_source_obsels):
                        current_noise += 1
                        LOG.debug("--- skipping %s (%s)", obs, current_noise)
                    if max_noise is not None and current_noise > max_noise:
                        LOG.debug("--- max_noise reached")
                        reset = True
                if reset:
                    current_source_obsels = []
                    current_begin = None
                    current_noise = 0
                    reset = False
                        

        cstate["last_seen"] = last_seen
        cstate["str_mon_tag"] = source_obsels.str_mon_tag
        cstate["current_source_obsels"] = current_source_obsels
        cstate["current_begin"] = current_begin
        cstate["current_noise"] = current_noise

        computed_trace.metadata.set((
            computed_trace.uri,
            METADATA.computation_state,
            Literal(json_dumps(cstate))
        ))
        return diag

    @staticmethod
    def _prepare_source_and_params(computed_trace, diag):
        """I check and prepare the data required by the method.

        I return the unique source of the computed trace, and a dict of
        useful parameters converted to the expected datatype. If this can not
        be done, I return ``(None, None)``.

        I also populate `diag` with error/warning messages.
        """
        sources = computed_trace.source_traces
        params = computed_trace.parameters_as_dict
        critical = False

        if len(sources) != 1:
            diag.append("Method Sequence expects exactly one source")
            critical = True

        for key, val in params.items():
            datatype = _PARAMETERS_TYPE.get(key)
            if datatype is None:
                diag.append("WARN: Parameter %s is not used by :sequence"
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

        if "target_otype" not in params:
            diag.append("Parameter 'target_otype' is required")
            critical = True

        if "components" not in params:
            diag.append("Parameter 'components' is required")
            critical = True

        if critical:
            return None, None
        else:
            return sources[0], params


def _parse_components_param(txt):
    comp = []
    for obsel_template in txt.split(";"):
        tests = []
        for test in obsel_template.split(","):
            if "=" in test:
                prop, val = test.split("=")
                tests.append((prop.strip(), val.strip(),))
            else:
                tests.append((test.strip(),))
        comp.append(tests)
    return comp

def _prepare_components(comp):
    ret = []
    for tests in comp:
        ret.append([])
        for test in tests:
            if len(test) == 1:
                ret[-1].append((RDF.type, URIRef(test[0])))
            else:
                ret[-1].append((URIRef(test[0]), Literal(test[1])))
    return ret
        

_PARAMETERS_TYPE = {
    "origin": Literal,
    "model": URIRef,
    "target_otype": URIRef,
    "components": _parse_components_param,
    "max_duration": int,
    "max_noise": int,
}



def start_plugin(_config):
    """I get the configuration values from the main kTBS configuration.

    .. note:: This function is called automatically by the kTBS.
              It is called once when the kTBS starts, not at each request.
    """
    register_builtin_method_impl(_SequenceMethod())

