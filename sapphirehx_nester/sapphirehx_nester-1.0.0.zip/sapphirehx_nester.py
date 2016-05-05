def print_lol(the_list):
    for letters in  the_list:
        if isinstance(letters,list):
            print_lol(letters)
        else:
            print(letters)
            