from lobgect import log

logger = log.Log(__name__)

@logger.log_variables
def check_list_value(unchecked_value, checked_base_object=[], known_good_options=[]):
    logger.debug('The unchecked value is \'{}\''.format(unchecked_value))
    checked_value = list(checked_base_object)
    unchecked_list = list(checked_base_object)

    if not unchecked_value:
        unchecked_list = known_good_options
    elif type(unchecked_value) is not list:
        unchecked_list = unchecked_value.split(',')
    else:
        unchecked_list = unchecked_value

    for unchecked_list_value in unchecked_list:
        if not unchecked_list_value or unchecked_list_value not in known_good_options:
            logger.warn('{} \'{}\' is not a known good value for this parameter'.format(type(unchecked_value), unchecked_value))
        else:
            checked_value.append(unchecked_list_value)

    logger.debug('The checked value is {}'.format(checked_value))

    if len(checked_value) > 0:
        return checked_value
    else:
        logger.warn('None of these values were any good, so you get all the right ones instead.')
        return known_good_options


@logger.log_variables
def check_value(unchecked_value, checked_base_object=None, default_value=None, known_good_options=[], expected_type=None):
    logger.debug('The unchecked value is \'{}\''.format(unchecked_value))
    checked_value = checked_base_object

    # Make sure the input is a good known value
    if not unchecked_value or (known_good_options and unchecked_value not in known_good_options):
        logger.warn('{} \'{}\' is not a known good value for this parameter'.format(type(unchecked_value), unchecked_value))
        checked_value = default_value
        logger.info('The parameter has instead been set as the default of \'{}\''.format(checked_value))

    # Or at least the right type
    elif expected_type:
        if type(unchecked_value) == expected_type:
            checked_value = unchecked_value
        else:  # If the input isn't the right type yet
            if expected_type == bool:
                logger.info("Boolean values can't be coerced from a string, exactly")
                checked_value = True if unchecked_value in ['true', 'True', '1', 't'] else False
            else:
                try:
                    expected_type(unchecked_value)  # try to coerce it
                    checked_value = unchecked_value # We need the string version for the API though
                except ValueError:  # Or ignore it
                    logger.warn('{} \'{}\' is not a known good value for this parameter'.format(type(unchecked_value), unchecked_value))
                    checked_value = default_value
                    logger.info('The parameter has instead been set as the default of \'{}\''.format(checked_value))

    else: checked_value = unchecked_value

    logger.debug('The checked value is \'{}\''.format(checked_value))

    return checked_value
