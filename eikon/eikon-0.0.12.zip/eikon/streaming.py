# coding: utf8
import websocket
try:
    import threading
except ImportError:
    import thread
from .tools import build_list
import eikon.Profile
import eikon.eikonError


class MarketPriceStream(object):
    """
    Open a market price stream.

    Parameters
    ----------
    rics: string or list
        List of RICs to retrieve market prices for.

    fields: string or list
        Specified the fields to retrieve.

    on_start: callable object
        Called when the stream is opened. This callback has no argument. Default: None

    on_update: callable object
        Called when an update is received.
        This callback receives an utf-8 string as argument.
        Default: None

    on_error: callable object
        Called when an error occurs.
        This callback receives Exception as argument
        Default: None

    on_close: callable object
        Called when subscription is closed.
        This callback has no argument.
        Default: None

    debug: bool
        When set to True, the json request and response are printed.

    Raises
    ------
    Exception
        If request fails or if Thomson Reuters Services return an error

    Examples
    --------
    >>> import eikon as ek
    >>> def on_update(msg):
        ... print(msg)
    >>> subscription = ek.MarketPriceStream(['VOD.L', 'EUR=', 'PEUP.PA', 'IBM.N'],
    >>>                                        ['DSPLY_NAME', 'BID', 'ASK'],
    >>>                                        on_update=on_update)
    >>> subscription.open()
    {"EUR=":{"DSPLY_NAME":"RBS          LON","BID":1.1221,"ASK":1.1224}}
    {"PEUP.PA":{"DSPLY_NAME":"PEUGEOT","BID":15.145,"ASK":15.155}}
    {"IBM.N":{"DSPLY_NAME":"INTL BUS MACHINE","BID":"","ASK":""}}
    ...
    """

    __all_subscriptions = {}

    def __init__(self, rics, fields, on_start=None, on_update=None, on_error=None, on_close=None, debug=False):
        self.rics = build_list(rics, 'rics')
        self.fields = build_list(fields, 'fields')
        self._on_start = on_start
        self._on_update = on_update
        self._on_error = on_error
        self._on_close = on_close
        self.ws = None
        self.debug = debug
        self.id = None

    def open(self):
        """
        Starts data streaming.
        """
        streaming_url = '{}rics={}&fields={}'.format(eikon.Profile.get_profile().get_streaming_url(),
                                                     ','.join(self.rics), ','.join(self.fields))
        self.ws = websocket.WebSocketApp(streaming_url, subprotocols=['tr_simple_json'],
                                         on_message=self.__on_message, on_error=self.__on_error,
                                         on_close=self.__on_close)
        self.ws.on_open = self.__on_open
        self.__register_subscription(self)
        self.ws.run_forever()

    def close(self):
        """
        Stops data streaming.
        """
        if self.ws.keep_running:
            self.ws.close()
            self.__unregister_subscription(self)

    @classmethod
    def __register_subscription(cls, subscription):
        if not subscription:
            raise eikon.eikonError.EikonError('Try to register unavailable subscription')
        subscription.id = threading.current_thread().ident
        if not subscription:
            raise eikon.eikonError.EikonError('Try to register unavailable subscription')
        if subscription.id in cls.__all_subscriptions:
            raise eikon.eikonError.EikonError('Subscription {} is already registered'.format(subscription.id))
        if subscription.debug:
            print('Register subscription id {}'.format(subscription.id))
        cls.__all_subscriptions[subscription.id] = subscription

    @classmethod
    def __unregister_subscription(cls, subscription):
        if not subscription:
            raise eikon.eikonError.EikonError('Try to unregister unavailable subscription')
        if subscription.id not in cls.__all_subscriptions:
            raise eikon.eikonError.EikonError('Try to unregister unknown subscription {}'.format(subscription.id))
        if subscription.debug:
            print('Unregister subscription id {}'.format(subscription.id))
        cls.__all_subscriptions.pop(subscription.id)

    @staticmethod
    def __on_open(ws):
        self = MarketPriceStream.__get_subscription()
        if self and self._on_start:
            self._on_start()

    @staticmethod
    def __on_message(ws, message):
        self = MarketPriceStream.__get_subscription()
        if self and self._on_update:
            self._on_update(message)

    @staticmethod
    def __on_error(ws, error):
        self = MarketPriceStream.__get_subscription()
        if self and self._on_error:
            self._on_error(error)

    @staticmethod
    def __on_close(ws):
        self = MarketPriceStream.__get_subscription()
        if self and self._on_close:
            self._on_close()

    @classmethod
    def __get_subscription(cls, subscription=None):
        if subscription:
            subscription_id = subscription.id
        else:
            subscription_id = threading.current_thread().ident

        return cls.__all_subscriptions.get(subscription_id, None)
