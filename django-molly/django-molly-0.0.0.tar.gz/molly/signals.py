from django.dispatch import Signal


application_started = Signal(providing_args=['application'])
