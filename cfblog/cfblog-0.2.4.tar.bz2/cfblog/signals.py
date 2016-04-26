from django.dispatch import Signal

"""
    Any handler of pre_publish_signal will return two values.
    And the results of all of these handlers will be available as a list.
    Frist element of the tuple should be boolean or None and
    the second one should be string.
    True for Success,
    False for Errors,
    None for Warnings
    e.g. [(True, "Success",), (False, "Tag Name: Error Message...",)...]
"""
pre_publish_signal = Signal(providing_args=["cms_page"])
post_publish_signal = Signal(providing_args=["cms_page"])
