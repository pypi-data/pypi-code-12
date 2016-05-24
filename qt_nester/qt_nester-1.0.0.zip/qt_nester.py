def print_lol(the_list):
    for i in the_list:
        if isinstance(i,list):
            print_lol(i)
        else:
            print(i)
js=["sb","db","sb",["nb","fuck"]]
print_lol(js)

