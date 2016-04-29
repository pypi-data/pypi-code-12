def _formatTrueFalse(b,trueValue,falseValue,noneValue):
    """Formats a boolean including a third option - None."""
    if value is None: return noneValue
    if value: return trueValue
    return falseValue


def formatYesNo(b,noneValue='No'):
    """Formats a boolean as Yes/No. By default, None is equivalent to False (No)."""
    return _formatTrueFalse('Yes','No',noneValue)


def formatTrueFalse(b,noneValue='False'):
    """Formats a boolean as True/False. By default, None is equivalent to False."""
    return _formatTrueFalse('True','False',noneValue)
