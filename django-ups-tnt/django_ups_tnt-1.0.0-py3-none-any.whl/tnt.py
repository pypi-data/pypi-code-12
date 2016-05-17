from . import settings
from .exceptions import UPSException
import datetime
import requests
import logging


logger = logging.getLogger(__name__)
ups_url = 'https://wwwcie.ups.com/json/TimeInTransit'


def prepare_location(location):
    ups_data = {'Address': {}}
    if location.get('city'):
        ups_data['Address']['City'] = location['city']
    if location.get('state_province_code'):
        ups_data['Address']['StateProvinceCode'] = location['state_province_code']
    if location.get('postal_code'):
        ups_data['Address']['PostalCode'] = location['postal_code']
    if location.get('country_code'):
        ups_data['Address']['CountryCode'] = location['country_code']
    return ups_data


def fetch_estimated_arrival_times(ship_from=None, ship_to=None, pickup_date=None):

    if ship_from:
        ship_from = prepare_location(ship_from)
    else:
        ship_from = settings.UPS_DEFAULT_SHIP_FROM

    if ship_to:
        ship_to = prepare_location(ship_to)
    else:
        ship_to = settings.UPS_DEFAULT_SHIP_TO

    if pickup_date is None:
        if isinstance(settings.UPS_BUFFER_DAYS, int):
            pickup_date = datetime.date.today() + datetime.timedelta(days=settings.UPS_BUFFER_DAYS)
        if callable(settings.UPS_BUFFER_DAYS):
            pickup_date = datetime.date.today() + datetime.timedelta(days=settings.UPS_BUFFER_DAYS())
    pickup_date = pickup_date.strftime('%Y%m%d')

    ups_data = {
        "Security": {
            "UsernameToken": {
                "Username": settings.UPS_USERNAME,
                "Password": settings.UPS_PASSWORD,
            },
            "UPSServiceAccessToken": {
                "AccessLicenseNumber": settings.UPS_ACCESS_LICENSE_NUMBER
            }
        },
        "TimeInTransitRequest": {
            "Request": {
                "TransactionReference": {
                    "CustomerContext": "TNT Request with Documents only Indicator"
                }
            },
            "ShipFrom": ship_from,
            "ShipTo": ship_to,
            "Pickup": {
                "Date": pickup_date
            },
            "ShipmentWeight": settings.UPS_DEFAULT_SHIPMENT_WEIGHT,
            "InvoiceLineTotal": settings.UPS_DEFAULT_INVOICE,
        }
    }

    try:
        res = requests.post(ups_url, json=ups_data)
    except requests.exceptions.RequestException:
        raise UPSException('UPS api is not responding')

    res_data = res.json()

    # This occurs when UPS API is down
    if res_data.get('Error'):
        error_details = res_data['Error']['Description']
        logger.error(error_details)
        raise UPSException(error_details)

    # This occurs when UPS API is up, but returns some error.
    if res_data.get('Fault'):
        error_details = res_data['Fault']['detail']['Errors']['ErrorDetail']['PrimaryErrorCode']['Description']
        raise UPSException(error_details)

    try:
        services = res_data['TimeInTransitResponse']['TransitResponse']['ServiceSummary']
    except KeyError:
        raise UPSException("Unexpected response received from UPS")

    estimated = None
    for service in services:
        estimate_date = service['EstimatedArrival']['Arrival']['Date']
        estimate_time = service['EstimatedArrival']['Arrival']['Time']
        estimated = "%s%s" % (estimate_date, estimate_time)
        estimated = datetime.datetime.strptime(estimated, '%Y%m%d%H%M%S')
        service['EstimatedArrival']['DateTime'] = estimated.isoformat()
    return res_data['TimeInTransitResponse']['TransitResponse']
