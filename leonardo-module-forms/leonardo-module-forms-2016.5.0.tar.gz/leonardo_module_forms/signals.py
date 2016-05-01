from django.dispatch import Signal

process_valid_form = Signal(
    providing_args=["widget", "request", "form_instance"])
