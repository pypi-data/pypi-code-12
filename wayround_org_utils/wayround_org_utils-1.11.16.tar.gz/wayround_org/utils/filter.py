
"""
Tools for filtering lists
"""

# TODO: future planed work
#       The aim is to create flexible and extensible filter function
#       to replace such in list.py and tarball.py


def filter_text_parse(filter_text):
    """
    Returns list of command structures

    ret = [
        dict(
            action   = '-' or '+',
            subject  = in ['path', 'filename', 'version', 'status'],
            function = <depends on subject> (no spaces allowed),
            data     = <depends on subject> (can contain spaces)
            )
        ]

    """
    ret = []

    lines = filter_text.splitlines()

    for i in lines:
        if i != '' and not i.isspace() and not i.startswith('#'):
            struct = i.split(' ', maxsplit=3)
            if not len(struct) == 4:
                logging.error("Wrong filter line: `{}'".format(i))
            else:
                struct = dict(
                    action=struct[0],
                    subject=struct[1],
                    function=struct[2],
                    data=struct[3]
                    )
                ret.append(struct)

    return ret


def filter(
        filter_text,
        full_source_list,
        subject_func_dict,
        compare_func_dict
        ):
    """
    parameters:
        filter_text,
            filter text str possibly supplyed by user

        full_source_list
            list with all possible variants

        subject_func_dict
            dict with subject functions
                keys   - are names of functions. any non-empty string without
                    spaces

                values - callables accepting following parameters:
                    1. this filter line subject func name
                        str with this function name
                    2. this filter line compare func name
                        which will be used
                    3. this one parameter is full item string which
                        is about to be checked.

                    callable must return some string value
                    which will be pased to comparison function
                    to be compared with it's parameter(s).
                    or return False to indicate what line already
                    didn't passed check on this stage, in which
                    case line being checked will be considered as absent in
                    full_source_list and will be minused

        compare_func_dict
            dict with comparisong functions
                keys   - are names of functions
                values - callables accepting following parameters:

                    1. this filter line compare func name
                        which will be used
                    2. this filter line subject func name
                        str with function name which was used for subject
                        devision
                    3. logical not: if true - will invert result
                    4. non case sensetivity - by default all functions
                        considered sensitive to case. this callabel can ignore
                        this parameter value if subject, for instance,
                        a numbers
                    5. filter parameter here goes 4-th value of of filter list 
                        line

    result: list with all, none or part of full_source_list items
    """

    parsed_filter_text = filter_text_parse(filter_text)
    
    

    return
