from .resource import List
from .resource import Find
from .resource import Update
from .resource import Create


class ActivitySubscription(List, Find, Update):
    """Activities class wrapping the REST activities endpoint
    """
    path = "activities-subscriptions"


class Notification(List, Find, Update):
    """Notifications class wrapping the REST notifications endpoint
    """
    path = "notifications"
