'''This is the "nester.py" module and it provides one funciton calld print_lol()
   which prints lists that may or may not include nested lists.'''
def   print_lol(the_list, level):
      """This function takes one positional argument called  "the_list",which
      is any Python list (of - rpssibly - nested lists ). Each data item in the
      provided list is (recursively) printed to the screen on it's own line.
      嵌套多层列表时，第二个参数level:0不打印制表符，1打印制表符"""
      for each_item in the_list:
            if isinstance(each_item, list):
                  if level > 0 :
                        level = level + 1 
                  print_lol(each_item, level)
                  
            else:
                  if level > 0:
                        for i in range(level - 1):
                              print("\t", end=' ')
                  print(each_item)
                  
                              
