''' This is  print_nlist.py module and it provides one function called
print_nlist() to print a list'''

# author = Patel Rahul Ganpatbhai, Asst. Prof., EC Dept., SPCE,Visnagar
# author e-mail: ec_rahul46@yahoo.com

# version   1.0.0 = printing element of nested list without indentation for
#                 nested elements
#           1.1.0 = modified for indentation for nesting elements by providing
#                   level value

def print_nlist(in_list,level):
    ''' This function accepted list as one argument and prints all the elements
 in the list on standard output'''
    for each_element in in_list:
        if(isinstance(each_element, list)):
            print_nlist(each_element, level+1)
        else:
            for tab_stop in range(level):
                print("\t", end=' ')
            print(each_element)

