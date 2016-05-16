

__version__ = "0.1.2"

token = None
api_base = 'https://api.figuredevices.com'

# Resources
from figure.resource import (
    Photobooth,
    Place,
    Event,
    TicketTemplate,
    Text,
    TextVariable,
    Image,
    ImageVariable,
    Portrait,
    PosterOrder,
    WifiNetwork,
    CodeList,
    User,
    Auth
)

from figure.error import (
    FigureError,
    APIConnectionError,
    BadRequestError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    RateLimitError,
    InternalServerError,
    NotAvailableYetError
)




