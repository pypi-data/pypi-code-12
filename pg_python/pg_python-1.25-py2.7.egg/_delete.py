def make_postgres_delete_statement(table, kv_map, debug):
    _prefix = "DELETE FROM "
    keys = ",".join(kv_map.keys())
    value_proxy_array = ["%s"] * len(kv_map)
    value_proxy_string = ", ".join(value_proxy_array)
    statement = " ".join([_prefix, table, "(", keys ,")", "VALUES", "(", value_proxy_string ,")"])
    if debug:
        print("Writing into Db: %s, %s" % (statement, kv_map.values()))
    return statement, kv_map.values()