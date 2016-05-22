'''This is the "nester.py" module and it provides on function called print_lol()
which prints lists that may or may not include nested lists.'''

movies = [
"The Holy Grail", 1975, "Terry Jones & Terry Gilliam", 91,
   ["Graham Chapman",
        ["Michael Palin", "John Cleese", "Terry Gilliam", "Eric Idle"]]]

def print_lol(the_list):
    """This function takes one positional argument called "the_list",which is any
    Python list(of -possibly - nested lists). Each data item in the provided list is 
    printed to screen on it's own line."""

    for each_item in the_list:
        if isinstance(print_lol,list):
            print_lol(each_item)
        else:
            print(each_item)

print_lol(movies)
