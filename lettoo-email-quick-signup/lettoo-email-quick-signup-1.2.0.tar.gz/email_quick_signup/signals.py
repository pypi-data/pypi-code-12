from django.dispatch import Signal

user_signed_up = Signal(providing_args=["request", "user"])

email_confirmed = Signal(providing_args=["email_address"])
email_confirmation_sent = Signal(providing_args=["confirmation"])
