"""
movies=["The Holy Grail",1975,"Terry Jones & Terry Gilliam",91,
        ["Graham Chapman",["Michael Palin","Jhon Cleese",
        "Terry Gilliam","Eric Idle","Terry Jones"]]]

for item in movies:
    if isinstance(item,list):
        for item1 in item:
            if isinstance(item1,list):
                for item2 in item1:vb
                    print (item2)
            else:
                print (item1)
    else:
        print (item)
"""
def print_lol(the_list):
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item)
        else:
            print (each_item)
