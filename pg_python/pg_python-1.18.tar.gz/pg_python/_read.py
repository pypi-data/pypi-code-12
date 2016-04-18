def make_postgres_read_statement(table, kv_map, keys_to_get, limit, order_by, order_type, debug, clause, group_by):
    _prefix = "SELECT"
    _table_string = " ".join(["FROM", table])
    _key_string = " AND ".join([ k + clause + "%s" for k in kv_map.keys()])
    statement = " ".join([_prefix, ", ".join(sorted(keys_to_get)), _table_string])
    if len(kv_map.keys()) > 0:
      statement = " ".join([_prefix, ", ".join(sorted(keys_to_get)), _table_string, "WHERE", _key_string])
    if group_by is not None:
        statement += " GROUP BY " + group_by
    if order_by is not None:
        statement += " ORDER BY " + order_by + " " + order_type
    if limit is not None:
        statement += " LIMIT " + str(limit)
    if debug:
      print("Reading From Db: %s, %s" %(statement, kv_map.values()))
    return statement, kv_map.values()

def prepare_values(all_values, keys_to_get):
    ret_val = []
    if all_values is None:
        return None
    k = sorted(keys_to_get)
    for row in all_values:
        row_kv = {}
        if len(row) == len(keys_to_get):
            for idx in range(0, len(row)):
                row_kv[k[idx]] = str(row[idx])
        else:
            print("Number of keys to be fetched are not correct")
            continue
        ret_val.append(row_kv)
    return ret_val
