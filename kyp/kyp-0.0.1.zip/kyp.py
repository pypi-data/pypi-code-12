
#C:\Users\KYP\Documents\DaumCloud\Bioinformatics_lecture\Note\hfpython

def print_101(the_list):
    for each_item in the_list:
        if isinstance(each_item, list):
            print_101(each_item)
        else:
            print(each_item)
            
