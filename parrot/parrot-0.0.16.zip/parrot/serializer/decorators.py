from parrot.exceptions import (
    SerializerItemBadValue,
    SerializerItemBadValueFromSource, SerializerSectionBadValueFromSource
)


def _validate_value(info, logger, exc):
    if not isinstance(info, dict):
        exc = exc(info)
        logger.warning(exc)
        raise exc


def _validate_value_from_url(info, url, logger, exc):
    if not isinstance(info, dict):
        exc = exc(info, url)
        logger.warning(exc)
        raise exc


def validate_item_sequence_with_section_info(logger):
    def decorator(func):
        def new_func(*pargs):
            item_url, item_info, section_url, section_info = pargs
            _validate_value_from_url(
                item_info, item_url, logger, SerializerItemBadValueFromSource
            )
            _validate_value_from_url(
                section_info, section_url, logger,
                SerializerSectionBadValueFromSource
            )
            return func(*pargs)
        return new_func
    return decorator


def validate_item_sequence_without_section_info(logger):
    def decorator(func):
        def new_func(*pargs):
            item_url, item_info = pargs
            _validate_value_from_url(
                item_info, item_url, logger, SerializerItemBadValueFromSource
            )
            return func(*pargs)
        return new_func
    return decorator


def validate_item_single(logger):
    def decorator(func):
        def new_func(item):
            _validate_value(item, logger, SerializerItemBadValue)
            return func(item)
        return new_func
    return decorator
