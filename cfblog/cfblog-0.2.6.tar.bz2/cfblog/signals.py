# coding=utf-8
from django.dispatch import Signal

"""
    pre_publish_signal handlers should return two values.
    Frist value should be boolean or None
    True for Success
    False for Errors
    None for Warnings

    Second value should be the corresponding message.
    e.g. [(True, "Success",), (False, "Invalid html",)...]
"""
pre_publish_signal = Signal(providing_args=["cms_page"])
post_publish_signal = Signal(providing_args=["cms_page"])
