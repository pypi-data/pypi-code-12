movies = ["The Holy Grail",1975,"Terry Jones & Terry Gilliam",91,["Graham Chapman",["Michael Palin","John Cleese","Terry Gilliam","Eric Idle","Terry Jones"]]]
def print_lol(the_list):
    for each_line in the_list:
        if isinstance(each_line,list):
            print_lol(each_line)
        else:
            print(each_line)

    
    
