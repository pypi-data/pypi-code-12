import itertools
def flatmap(f, items):
    return itertools.chain.from_iterable(map(f, items))

from transcriptic import *
connect()
from transcriptic import api

query = 'water'
rs_water = api.resources(query)
kit_water = api.kits(query)

flat_items = list(flatmap(lambda x: [{"name": y["resource"]["name"],
                                 "id": y["resource"]["id"],
                                 "vendor": x["vendor"]["name"] if "vendor" in x.keys() else ''}
                                for y in x["kit_items"] if
                                     (y["provisionable"] and not y["reservable"])],
                          kit_water["results"]))

rs_id_list = [rs["id"] for rs in rs_water["results"]]

matched_items = []
for item in flat_items:
    if item["id"] in rs_id_list and item not in matched_items:
        matched_items.append(item)
