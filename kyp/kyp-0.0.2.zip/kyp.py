
#C:\Users\KYP\Documents\DaumCloud\Bioinformatics_lecture\Note\hfpython

def print_101(the_list, level):
    for each_item in the_list:
        if isinstance(each_item, list):
            print_101(each_item, level + 1)
        else:
            for tap_stop in range(level):
                print '\t', 
            print(each_item)
            
