from django.dispatch import Signal

# Sent when a user first registers
user_registered = Signal(providing_args=["request", "profile"])

# Sent when a user sets their password on the page sent to them by email
user_password_set = Signal(providing_args=["request", "profile"])

user_activated = Signal(providing_args=["request", "profile"])

user_rejected = Signal(providing_args=["request", "profile"])