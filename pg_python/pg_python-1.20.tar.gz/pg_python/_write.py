def make_postgres_write_statement(table, kv_map, debug=True):
    _prefix = "INSERT INTO"
    keys = ",".join(kv_map.keys())
    values = []
    for value in kv_map.values():
      if type(value) == bool:
        if value == True:
          values.append('true')
        else:
          values.append('false')
      else:
        values.append(value)
  
    value_proxy_array = ["%s"] * len(kv_map)
    value_proxy_string = ", ".join(value_proxy_array)
    statement = " ".join([_prefix, table, "(", keys ,")", "VALUES", "(", value_proxy_string ,")"])
    if debug:
      print("Writing into Db: %s, %s" % (statement, values))
    return statement, kv_map.values()
