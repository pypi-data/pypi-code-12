"""nester模块，提供了一个print_lol的函数，该函数作用是打印列表，包括列表中的列表"""

def print_lol(all_items):
    """print_lol，需要输入一个列表，函数将其和内嵌列表进行打印"""
    for each_item in all_items:
        if isinstance(each_item, list):
            print_lol(each_item)
        else:
            print(each_item)

'''movies = ["The Holy Grail", 1975, "Terry Jomes & Terry Gilliam", 91, "Graham Chapean",
          ["Michael Palin", "John Cleese", "Terry Gilliam", "Eric Idle"]]
print_lol(movies)
'''
