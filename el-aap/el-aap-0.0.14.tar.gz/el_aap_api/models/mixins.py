__author__ = 'schlitzer'

from el_aap_api.errors import *
import pymongo


class FilterMixIn(object):
    @staticmethod
    def _filter_boolean(query, field, selector):
        if selector is None:
            return
        if selector in [True, 'true', 'True', '1']:
            selector = True
        elif selector in [False, 'false', 'False', '0']:
            selector = False
        else:
            raise InvalidSelectors('Selector is not a boolean')
        query[field] = selector

    @staticmethod
    def _filter_list(query, field, selector):
        if not selector:
            return
        if type(selector) is not list:
            selector = list(set(selector.split(',')))
        query[field] = {'$in': selector}

    @staticmethod
    def _filter_re(query, field, selector):
        if not selector:
            return
        query[field] = {'$regex': selector}


class PaginationSkipMixIn(object):
    pagination_limit = 1000
    pagination_steps = [10, 25, 50, 100, 250, 500, 1000]

    def _pagination_skip(self, page=None, limit=None):
        if not page:
            page = 0
        else:
            page = int(page)
        if not limit:
            limit = self.pagination_limit
        else:
            limit = int(limit)
        return page * limit

    def _pagination_limit(self, limit=None):
        if not limit:
            limit = self.pagination_limit
        else:
            limit = int(limit)
            if limit not in self.pagination_steps:
                raise InvalidPaginationLimit(self.pagination_steps)
        return limit


class ProjectionMixIn(object):
    projection_fields = {}

    def _projection(self, fields=None):
        if not fields:
            return self.projection_fields
        fields = fields.split(sep=',')
        for field in fields:
            if field not in self.projection_fields:
                raise InvalidFields('{0} is not a valid field'.format(field))
        result = {}
        for field in fields:
            result[field] = 1
        return result


class SortMixIn(object):
    sort_fields = []

    def _sort(self, sort=None, strict_order=True):
        if not sort:
            return self.sort_fields
        result = []
        items = []
        sort = sort.split(sep=',')
        for item in sort:
            if item.startswith('-'):
                order = pymongo.DESCENDING
                item = item[1:]
            else:
                order = pymongo.ASCENDING
            self._sort_valid_criteria(item)
            if item not in items:
                items.append(item)
            else:
                raise InvalidSortCriteria('{0} has been specified multiple times'.format(item))
            result.append((item, order))
        if strict_order:
            result = self._sort_strict_order(result)
        return result

    def _sort_valid_criteria(self, item):
        for allowed in self.sort_fields:
            if allowed[0] == item:
                return
        raise InvalidSortCriteria('{0} is not allowed as sort criteria'.format(item))

    def _sort_strict_order(self, items):
        for element in range(len(self.sort_fields)):
            try:
                if not self.sort_fields[element][0] == items[element][0]:
                    raise InvalidSortCriteria('sort criteria number {0} should be {1} but is {2}'.format(
                        element, self.sort_fields[element][0], items[element][0]
                    ))
            except IndexError:
                items.append(self.sort_fields[element])
        return items
