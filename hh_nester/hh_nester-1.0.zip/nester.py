''' the nester module only contains one function
    print_lol() which is given a list to print'''


def print_lol(lst):
  ''' the print_lol() function prints a given list
  if the list contains nested lists it prints them as well
  this is accomplished using recursion
  '''
  for item in lst:
    if isinstance(item, list):
      print_lol(item)
    else:
      print(item)
