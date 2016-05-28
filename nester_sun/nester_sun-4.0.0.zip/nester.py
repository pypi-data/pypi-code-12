'''
Created on May 27, 2016

@author: su005ku
'''
def print_list(nester_list):
    for list_item in nester_list:
        if isinstance(list_item, list):
            print_list(list_item)
        else:
            print(list_item)