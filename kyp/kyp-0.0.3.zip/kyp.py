
#C:\Users\KYP\Documents\DaumCloud\Bioinformatics_lecture\Note\hfpython

def print_101(the_list, indent = False, level = 0):
    for each_item in the_list:
        if isinstance(each_item, list):
            print_101(each_item, indent, level + 1)
        else:
            if indent:
                for tap_stop in range(level):
                    print '\t', 
            print(each_item)
            
