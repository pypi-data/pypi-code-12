import django.dispatch

request_done = django.dispatch.Signal(providing_args=["response"])
request_failed = django.dispatch.Signal(providing_args=["response", "error"])
