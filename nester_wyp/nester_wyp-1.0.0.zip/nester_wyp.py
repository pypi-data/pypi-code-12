"""This module is to print all the items in a list,
and any sub items if the parent item were a list. 
"""
def print_lol (the_list):
 for each_item in the_list:
  if isinstance(each_item, list):
   print_lol(each_item)
  else:
   print(each_item)


   
