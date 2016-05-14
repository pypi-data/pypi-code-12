"""This is my first py类型的文件"""


def print_list(the_list):
    """this function takes one positional argument called "the list",which is any Python list"""
    for item in the_list:
        if isinstance(item, list):
            print_list(item)
        else:
            print(item)


movies = ["The Holy Grail", 1975, "Terry Jones & Terry Gilliam", 91,
          ["Graham Chapman", ["Michael Palin", "John Cleese",
                              "Terry Gilliam", "Eric Idle", "Terry Jones"]]]

print_list(movies)
