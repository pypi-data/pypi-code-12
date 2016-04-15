"""This is a good module, the name is print_lol(), you can use it for list print"""
def print_lol(the_list):
  """ddd"""
  #just try
  for each_item in the_list:
    if isinstance(each_item, list):
      print_lol(each_item)
    else:
      print(each_item)
