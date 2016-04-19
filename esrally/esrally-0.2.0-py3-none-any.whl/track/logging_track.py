from esrally.track import track


class DefaultQuery(track.Query):
    def __init__(self):
        track.Query.__init__(self, "default")

    def run(self, es):
        return es.search(index='logs')


class TermQuery(track.Query):
    def __init__(self):
        track.Query.__init__(self, "term")

    def run(self, es):
        return es.search(index='logs', doc_type='type', q='message:en')


class PhraseQuery(track.Query):
    def __init__(self):
        track.Query.__init__(self, "phrase")

    def run(self, es):
        return es.search(index='logs', doc_type='type', q='"ab_international.languages.ja+off"')


class HourlyAggQuery(track.Query):
    def __init__(self):
        track.Query.__init__(self, "hourly_agg")

    def run(self, es):
        return es.search(index='logs', doc_type='type', body='''
  {
      "size": 0,
      "aggregations": {
    "by_hour": {
        "date_histogram": {
      "field": "@timestamp",
      "interval": "hour"
        }
    }
      }
  }''')


class ScrollQuery(track.Query):
    PAGES = 25
    ITEMS_PER_PAGE = 1000

    def __init__(self):
        track.Query.__init__(self, "scroll", normalization_factor=self.PAGES)

    def run(self, es):
        r = es.search(index='logs', doc_type='type', sort='_doc', scroll='10m', size=self.ITEMS_PER_PAGE)
        # Note that starting with ES 2.0, the initial call to search() returns already the first result page
        # so we have to retrieve one page less
        for i in range(self.PAGES - 1):
            hit_count = len(r['hits']['hits'])
            if hit_count == 0:
                # done
                break
            r = es.scroll(scroll_id=r['_scroll_id'], scroll='10m')


track.Track(
    name="logging",
    description="This test indexes 6.9M short documents (log lines, total 14 GB json) using 8 client threads and 5000 docs per bulk request"
                " against a single or two nodes running on a dual Xeon X2699 (36 real cores, 72 with hyperthreading) and 256 GB RAM.",
    source_root_url="s3://users.elasticsearch.org/etsy/jls",
    index_name="logs",
    type_name="type",
    number_of_documents=6881288,
    compressed_size_in_bytes=1843865288,
    uncompressed_size_in_bytes=14641454513,
    document_file_name="web-access_log-20140408.json.gz",
    mapping_file_name="mappings.json",
    # for defaults alone, it's just around 20 minutes, for all it's about 60
    estimated_benchmark_time_in_minutes=20,
    # Queries to use in the search benchmark
    queries=[DefaultQuery(), TermQuery(), PhraseQuery(), HourlyAggQuery(), ScrollQuery()],
    track_setups=track.track_setups
)
