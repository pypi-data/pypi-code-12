from rest_framework.exceptions import APIException


class UPSException(APIException):
    status_code = 400
    default_detail = "Problem with UPS API"
