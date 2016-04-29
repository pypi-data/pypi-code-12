
def print_list(lista):
    for each_item in lista:
        if isinstance(each_item,list):
            print_list(each_item)
        else:
            print(each_item)
