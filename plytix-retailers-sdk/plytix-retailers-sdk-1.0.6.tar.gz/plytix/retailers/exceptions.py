class PlytixRetailersAPIError(Exception):
    pass


class ClientNotValidError(PlytixRetailersAPIError):
    pass


class IncorrectDataError(PlytixRetailersAPIError):
    pass


class ClientNotInitializedError(PlytixRetailersAPIError):
    pass


class BadResponseError(PlytixRetailersAPIError):
    pass


class BadRequestError(PlytixRetailersAPIError):
    pass


class MetadataValueError(PlytixRetailersAPIError):
    pass


class ResourceNotFoundError(PlytixRetailersAPIError):
    pass