from __future__ import print_function
import pandas as pd


def query_sf(salesforce_obj=None, query=None, keep_attributes=False, print_stats=False):
    sfq = SalesForceQuery(salesforce_obj)
    df = sfq.query_sf(query=query, keep_attributes=keep_attributes, print_stats=print_stats)
    return df

class SalesForceQuery(object):

    def __init__(self, salesforce_obj=None):
        if salesforce_obj:
            self.sf = salesforce_obj
        else:
            self.sf = None

    def query_sf(self, salesforce_obj=None, query=None, keep_attributes=False, print_stats=False):

        if not salesforce_obj:
            salesforce_obj = self.sf
            if not salesforce_obj:
                raise AttributeError("No Salesforce Object was passed.")
        if not query:
            raise AttributeError("No query was passed.")

        query_result = salesforce_obj.query_all(query)

        if query_result['totalSize'] == 0:
            return "Query returns 0 results"

        if print_stats:
            print("Returned: " + str(query_result['totalSize']) + " records")

        df = pd.DataFrame(query_result['records'])

        # If a query has a field from another table, the col is stored as a nested dictionary.
        # This brings the data out into its own column, and gets rid of the old one.
        query_2nd_processing = []
        values, _ = query.split("FROM")
        values = values.replace("SELECT ", "")
        for field_name in values.split(", "):
            if "." in field_name:
                query_2nd_processing.append(field_name.split("."))

        col_list_to_delete = []
        for col in query_2nd_processing:
            orig_name, col_name, new_name = col
            col_list_to_delete.append(col_name)
            df[orig_name + '_' + new_name] = df[col_name].apply(lambda x: x[new_name])

        for col in set(col_list_to_delete):
            df = df.drop([col], axis=1)

        if not keep_attributes:
            df = df.drop(['attributes'], axis=1)

        return df
