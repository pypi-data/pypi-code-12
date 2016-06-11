from qtk.data.bbg.defs import SECURITY_DATA, FIELD_DATA
import blpapi


def request_handler(refservice):
    request = refservice.createRequest("ReferenceDataRequest")
    request.append("securities", "YCGT0025 Index")
    request.append("fields", "CURVE_MEMBERS")
    return request


def event_handler(event, output):
    event_type = event.eventType()
    if (event_type == blpapi.Event.RESPONSE) or (event_type == blpapi.Event.PARTIAL_RESPONSE):
        #print i,"|",event.eventType(),"|", msg
        for msg in event:
            data = msg.getElement(SECURITY_DATA).getValueAsElement(0).getElement(FIELD_DATA)
            output["fieldData"] = data



def error_handler(e):
    pass
