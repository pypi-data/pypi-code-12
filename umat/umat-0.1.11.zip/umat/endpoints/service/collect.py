from functools import partial
from itertools import chain
from math import ceil
from multiprocessing.dummy import Pool
from .request import request


def parallel(worker):
    def wrapper(self, args):
        pool = Pool(len(args))
        results = pool.map(partial(worker, self), args)
        pool.close()
        pool.join()
        return list(chain.from_iterable(results))
    return wrapper


class Collector(object):
    MAT_APT_MAX_LIMIT = 2000

    def __init__(self, params, count_url, find_url):
        self.params = params
        self.params['limit'] = self.MAT_APT_MAX_LIMIT
        self.count_url = count_url
        self.find_url = find_url

    def collect(self):
        pages = range(1, self.count() + 1)
        params = [self.get_find_params(n) for n in pages]
        data = self.find(params)
        return data

    def count(self):
        params = self.get_count_params()
        response_json = request(self.count_url, params=params)
        n_results = float(response_json['data'])
        n_pages = ceil(n_results / self.params['limit'])
        n_pages = int(n_pages)
        return n_pages

    @parallel
    def find(self, params):
        response_json = request(self.find_url, self.params)
        return response_json['data']

    def get_count_params(self):
        params = self.params.copy()
        params.pop('limit', None)
        params.pop('page', None)
        return params

    def get_find_params(self, thread_n):
        params = self.params.copy()
        params['page'] = thread_n
        return params
