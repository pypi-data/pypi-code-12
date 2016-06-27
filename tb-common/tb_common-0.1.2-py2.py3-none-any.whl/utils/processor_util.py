__author__ = 'hiepsimu'


class ProcessorUtils(object):
    @staticmethod
    def map_list(lst, field_name):
        """
        Create hashtable from list

        map_list([{a: 1, b: 2}, {a: 3, b: 4}], 'a') => {1: {a: 1, b:2}, 3: {a: 3, b: 4}}
        """
        ret = {}
        for item in lst:
            if field_name in item:
                ret[item[field_name]] = item

        return ret