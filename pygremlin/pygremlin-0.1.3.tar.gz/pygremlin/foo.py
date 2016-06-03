#!/usr/bin/python
import json
import sys
from elasticsearch import Elasticsearch
import pprint

es = Elasticsearch(hosts=['192.168.33.33:30200'])
d = es.search(index="nginx", body={
    "size" : 500,
    "query" : {
        "bool" : {
            "must" : [
                { "prefix" : { "src" : "productpage" }},
                { "prefix" : { "dst" : "reviews" }},
                { "match" : { "http_cookie" : "user=jason" }},
                { "range" : { "@timestamp" : {"gte" : "2016-06-02"}}}
            ]
        }
    }
})

pprint.pprint(d)

# with open("checklist.json") as fp:
#     checklist = json.load(fp)
# ac = A8AssertionChecker(checklist['log_server'], None, header="Cookie", pattern="user=jason")
# results = ac.check_assertions(checklist, all=True)
# exit_status = 0

# for check in results:
#     print 'Check %s %s %s:%s' % (check.name, check.info, passOrfail(check.success), check.errormsg)
#     if not check.success:
#         exit_status = 1
# sys.exit(exit_status)
                                                                        
