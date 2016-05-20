import tcell_agent.agent

from tcell_agent.sensor_events import AppSensorEvent

def sendEvent(
    meta,
    detection_point,
    parameter,
    data,
    payload=None,
    pattern=None):
    tcell_agent.agent.TCellAgent.send(AppSensorEvent(
        detection_point,
        parameter,
        meta.location,
        meta.remote_address,
        meta.route_id,
        data,
        meta.method,
        payload=payload,
        user_id=meta.user_id,
        hmacd_session_id=meta.session_id,
        pattern=pattern
    ))
