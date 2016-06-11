"""
This file handles Interest Rate Curves
"""
import blpapi
from .defs import SECURITY_DATA, FIELD_DATA, CURVE_MEMBERS, SECURITY
from .mapper import bbg_to_std

_CURVE_MEMBER_DATA0 = ["CPN", "CPN_FREQ", "ISSUE_DT", "MATURITY",
                       "DAY_CNT_DES", "PX_LAST", "SECURITY_TYP", "SECURITY_TYP2",
                       "BPIPE_REFERENCE_SECURITY_CLASS"]


def get_ircurve_members_request_handler(index_ticker, curve_date):
    def request_handler(session):
        refservice = session.getService("//blp/refdata")
        request = refservice.createRequest("ReferenceDataRequest")
        request.append("securities", index_ticker)
        request.append("fields", "CURVE_MEMBERS")
        overrides = request.getElement("overrides")
        override_field = overrides.appendElement()
        override_field.setElement("fieldId","CURVE_DATE")
        override_field.setElement("value", curve_date.strftime("%Y%m%d"))
        return request
    return request_handler


def ircurve_members_event_handler(event, output):
    event_type = event.eventType()
    if (event_type == blpapi.Event.RESPONSE) or (event_type == blpapi.Event.PARTIAL_RESPONSE):
        for msg in event:
            field_data = msg.getElement(SECURITY_DATA).getValueAsElement(0).getElement(FIELD_DATA)

            curve_members = field_data.getElement(CURVE_MEMBERS)
            member_tickers = [curve_members.getValueAsElement(i).getElementAsString("Curve Members")
                              for i in range(curve_members.numValues())]
            output["tickers"] = member_tickers


def get_ircurve_member_data_request_handler(tickers, asof_date):
    def request_handler(session):
        refservice = session.getService("//blp/refdata")
        #request = refservice.createRequest("HistoricalDataRequest")
        request = refservice.createRequest("ReferenceDataRequest")
        for ticker in tickers:
            request.append("securities", ticker)

        for field in _CURVE_MEMBER_DATA0:
            request.append("fields", field)
        dt = asof_date.strftime("%Y%m%d")
        #request.set("startDate", dt)
        #request.set("endDate", dt)
        return request
    return request_handler


def ircurve_members_data_event_handler(event, output):
    event_type = event.eventType()
    if (event_type == blpapi.Event.RESPONSE) or (event_type == blpapi.Event.PARTIAL_RESPONSE):
        for msg in event:
            print msg
            print "----------------"
            security_data = msg.getElement(SECURITY_DATA)
            for i in range(security_data.numValues()):
                element = security_data.getValueAsElement(i)
                security = element.getElementAsString(SECURITY)
                field_data = element.getElement(FIELD_DATA)
                data_dict = {}
                for f in _CURVE_MEMBER_DATA0:
                    try:
                        val = field_data.getElementAsString(f)
                        key = bbg_to_std(f)
                    except Exception as e:
                        val = None

                    data_dict[key.id()] = val
                output[security] = data_dict