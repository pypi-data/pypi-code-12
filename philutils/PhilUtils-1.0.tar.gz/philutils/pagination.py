#!/usr/bin/env python

def check_if_type(variable, name, expected_type):
    if not isinstance(variable, expected_type):
        message = "'%s' is a %s when it should be a %s"
        raise TypeError(message % (name, type(variable), expected_type))


def validate_input(num_pages, current_page, number_surrounding_pages):
    check_if_type(num_pages, 'num_pages', int)
    check_if_type(current_page, 'current_page', int)
    check_if_type(number_surrounding_pages, 'number_surrounding_pages', int)
    if num_pages < 0:
        raise ValueError("'num_pages' must be at least zero")
    if current_page < 0:
        raise ValueError("'current_page' must be at least zero")
    if number_surrounding_pages < 0:
        raise ValueError("'number_surrounding_pages' must be at least zero")
    if current_page > num_pages:
        message = "'current_page' must be less than or equal to 'num_pages'"
        raise ValueError(message)


def get_display_pages(num_pages, current_page, number_surrounding_pages=2):
    validate_input(num_pages, current_page, number_surrounding_pages)

    start_range = set(range(1, number_surrounding_pages + 2))
    mid_range = set(range(
        current_page - number_surrounding_pages,
        current_page + number_surrounding_pages + 1))
    end_range = set(range(num_pages - number_surrounding_pages, num_pages + 1))

    combined_set = start_range.union(mid_range).union(end_range)
    sorted_page_list = sorted(list(combined_set))

    previous_page_number = 1
    result = []
    for page in sorted_page_list:
        if page > 0 and page <= num_pages:
            if page - previous_page_number > 1:
                result.append(dict(type="ellipsis"))
            previous_page_number = page
            is_current = page == current_page
            result.append(dict(type="link", page=page, is_current=is_current))
    return result
