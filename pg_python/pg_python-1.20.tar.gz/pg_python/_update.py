def make_postgres_update_statement(table, kv_map, where_kv_map, debug = True):
    _prefix = "UPDATE"
    keys = ",".join([k + "=%s" for k in kv_map.keys()])
    where_keys = ",".join([k + "=%s" for k in where_kv_map.keys()])
    value_proxy_array = ["%s"] * len(kv_map)
    value_proxy_string = ", ".join(value_proxy_array)
    statement = " ".join([_prefix, table, "SET", keys, "WHERE", where_keys])
    if debug:
      print("Updating into Db: %s, %s" %(statement, kv_map.values() + where_kv_map.values()))
    return statement, kv_map.values() + where_kv_map.values()
