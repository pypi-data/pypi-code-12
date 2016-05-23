def check_math(expression, answer):
    """Check a math expression with an answer.

    Parameters
    ----------
    expression : math equation
        The math expression to check.
    answer : numeric
        The answer to the expression.

    Returns
    -------
    bool
        True if answer matches evaluated equation, False is not.
    """
    return expression == answer
