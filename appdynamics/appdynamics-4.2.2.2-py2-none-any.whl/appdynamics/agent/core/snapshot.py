# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Converts snapshot information into data structures for reporting.

"""

from collections import deque
import os

from appdynamics import config
from appdynamics.lib import itervalues, make_name_value_pairs, u2b

from appdynamics.agent import pb
from appdynamics.agent.core import correlation
from appdynamics.agent.models import callgraph, errors, exitcalls


REQUIRED = pb.SnapshotInfo.REQUIRED
ERROR = pb.SnapshotInfo.ERROR
SLOW = pb.SnapshotInfo.SLOW
CONTINUING = pb.SnapshotInfo.CONTINUING


def is_partial_snapshot(trigger):
    return trigger not in (CONTINUING, REQUIRED)


def make_snapshot_info_dict(bt):
    return {
        'trigger': bt.snapshot_trigger,
        'snapshot': make_snapshot_dict(bt),
    }


def make_snapshot_dict(bt):
    call_graph = make_call_graph_dict(bt.sample_data, bt.timer.duration_ms, bt._exit_calls,
                                      include_internal_frames=config.INCLUDE_AGENT_FRAMES)
    snapshot = {
        'snapshotGUID': bt.snapshot_guid,
        'timestamp': bt.snapshot_start_time_ms,
        'callGraph': call_graph,
        'errorInfo': errors.make_error_info_dict(bt.errors),
        'exceptionInfo': errors.make_exception_info_dict(bt.exceptions),
        'processID': os.getpid(),
        # CORE-48460 We have to add all the exit calls again, even though we
        # may have added them to the callGraph already.
        'exitCalls': [make_snapshot_exit_call_dict(exit_call) for exit_call in itervalues(bt._exit_calls)],
    }

    if bt.request:
        snapshot['httpRequestData'] = make_snapshot_http_request_data(bt.request, bt.status_code, bt.http_data_gatherer)

    if bt.snapshot_user_data:
        snapshot['methodInvocationData'] = make_name_value_pairs(bt.snapshot_user_data)

    if bt.cross_app_correlation:
        snapshot['upstreamCrossAppSnapshotGUID'] = bt.cross_app_correlation[correlation.GUID_KEY]

    if bt.eum_guid:
        snapshot['eumGUID'] = bt.eum_guid

    return snapshot


def make_snapshot_http_request_data(request, status_code, gatherer):
    http_data = {
        'url': request.url.encode('utf-8'),
        'requestMethod': request.method,
        'responseCode': status_code,
    }

    if gatherer:
        http_data['cookies'] = make_name_value_pairs(
            dict((key, request.cookies[key]) for key in gatherer.cookies if key in request.cookies))
        http_data['headers'] = make_name_value_pairs(
            dict((key, request.headers[key]) for key in gatherer.headers if key in request.headers))
        http_data['httpParams'] = make_name_value_pairs(
            dict((name, request.args[key]) for key, name in gatherer.request_params if key in request.args))

    return http_data


def make_call_graph_dict(sample_data, total_time_taken_ms, exit_calls, include_internal_frames=False):
    """Make a dict representing a pb.CallGraph.

    This takes a SampleData, converts it into a call graph, then flattens that
    call graph using a level order traversal for packing into the protobuf.
    The call graph will have a synthetic root '{request}' that contains all of
    the time taken by the BT.

    If there are no samples in sample_data, then we return immediately.

    Parameters
    ----------
    sample_data : appdynamics.agent.models.callgraph.SampleData
        The sample data collected by the profiler
    total_time_taken_ms : int
        The precise time taken in the business transaction.

    Other Parameters
    ----------------
    include_internal_frames : bool, optional

    Returns
    -------
    dict
        A dict suitable for populating a ``pb.CallGraph``.

    """
    if not sample_data:
        return {}

    root = callgraph.make_call_graph(sample_data, total_time_taken_ms, include_internal_frames=include_internal_frames)

    # We always create a synthetic root that receives special treatment.
    # Add any unassigned exit calls to the root node.
    elements = [{
        'type': pb.CallElement.PY,
        'method': '{request}',
        'numChildren': len(root.children),
        'timeTaken': root.time_taken_ms,
        'exitCalls': [
            make_snapshot_exit_call_dict(exit_call)
            for exit_call in itervalues(exit_calls)
            if not exit_call.was_assigned
        ],
    }]

    q = deque(root.children)

    # Flatten the call graph using a level-order traversal.
    while q:
        node = q.popleft()
        q.extend(node.children)
        element = make_call_element_dict(node)
        elements.append(element)

    return {'callElements': elements}


def make_call_element_dict(call):
    frame = call.frame

    return {
        'type': pb.CallElement.PY,
        'numChildren': len(call.children),
        'timeTaken': call.time_taken_ms,
        'klass': frame.class_name,
        'method': frame.name,
        'fileName': frame.filename,
        'lineNumber': frame.lineno,
        'exitCalls': [make_snapshot_exit_call_dict(exit_call) for exit_call in call.exit_calls],
    }


def make_snapshot_exit_call_dict(exit_call):
    properties = make_name_value_pairs(exit_call.backend.identifying_properties, exit_call.backend.optional_properties)

    result = {
        'backendIdentifier': exitcalls.make_backend_identifier_dict(exit_call.backend),
        'timeTaken': exit_call.time_taken_ms,
        'sequenceInfo': exit_call.sequence_info,
        'count': exit_call.num_calls,
        'properties': properties,
    }

    if exit_call.operation:
        result['detailString'] = u2b(exit_call.operation)

    return result


def is_db_backend(exit_call):
    return exit_call.backend.exit_point_type == exitcalls.EXIT_DB


def make_snapshot_db_calls_dicts(bt):
    return [
        {
            'backendIdentifier': exitcalls.make_backend_identifier_dict(db.backend),
            'sqlString': u2b(db.operation),
            'count': db.num_calls,
            'totalTimeTakenMS': db.time_taken_ms,
            'minTimeMS': db.min_time_taken_ms,
            'maxTimeMS': db.max_time_taken_ms,
            'sequenceInfo': str(db.id),
            'boundParameters': make_bound_parameters_dict(db.params),
        }
        for db in filter(is_db_backend, itervalues(bt._exit_calls))
    ]


def make_bound_parameters_dict(params):
    return None  # TODO: Implement parameter tracking
