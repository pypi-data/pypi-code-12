def head(list1: list) -> object:
    """Return the head of a list.

    If the input list is empty, then return `None`.
    
    :param list list1: input list 

    :return: the first item
    :rtype: object

    >>> head([])
    None

    >>> head([1,2,3])
    1
    """
    if len(list1) == 0:
        return None
    else:
        return list1[0]
