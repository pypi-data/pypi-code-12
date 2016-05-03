''' This is  print_nlist.py module and it provides one function called
print_nlist() to print a list'''

# author = Patel Rahul Ganpatbhai, Asst. Prof., EC Dept., SPCE,Visnagar
# author e-mail: ec_rahul46@yahoo.com

# version   1.0.0 = printing element of nested list without indentation for
#                 nested elements
#           1.1.0 = modified for indentation for nesting elements by providing
#                   level value and only positive values of level accepted.
#           1.2.0 = made level and optional argument with level's default value 0
#           1.3.0 = made indention optional, with default vale as False

def print_nlist(in_list,indent = False,level=0):
    ''' This function accepted list as one argument and prints all the elements
 in the list on standard output'''
    if (level < 0):
        print('level negative, rounded to zero')
        level = 0
    for each_element in in_list:
        if(isinstance(each_element, list)):
            print_nlist(each_element, indent, level+1)
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t", end=' ')
            print(each_element)

