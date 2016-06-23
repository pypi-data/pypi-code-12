def tail(list1: list) -> list:
    """Return the tail of a list 

    Return the rest of the list (beyond the first element).
    If the input list is empty or has only one element, then return `[]`.
    
    :param list list1: input list 

    :return: a new list 
    :rtype: list

    >>> tail([])
    []

    >>> tail([1])
    []

    >>> tail([1,2,3])
    [2,3]
    """
    if len(list1) <= 1:
        return []
    else:
        return list1[1:]
