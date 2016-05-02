''' This is  print_nlist.py module and it provides one function called
print_nlist() to print a list'''

def print_nlist(in_list):
    for each_element in in_list:
        if (isinstance(each_element,list)):
            print_nlist(each_element)
        else:
            print(each_element)
