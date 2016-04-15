from django.dispatch import Signal

user_signed_up = Signal(providing_args=["request", "user"])

phone_confirmed = Signal(providing_args=["phone_number"])
phone_confirmation_sent = Signal(providing_args=["confirmation"])
