import dependency_injector.containers as containers
import dependency_injector.providers as providers

from messenger_sdk.config import Config
from messenger_sdk.api_client import ApiClient
from messenger_sdk.events import EventFactory
from messenger_sdk.fb_manager import FbManager
from messenger_sdk.log import Log


class BaseContainer(containers.DeclarativeContainer):
    config = providers.Singleton(Config)
    api_client = providers.Singleton(ApiClient)
    event_factory = providers.Singleton(EventFactory)
    log = providers.Singleton(Log, config)
    fb_manager = providers.Factory(FbManager, api_client, config)
