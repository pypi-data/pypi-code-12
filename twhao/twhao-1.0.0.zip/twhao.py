"""阿萨德发挥空间老师"""
def fun_book(the_list):
    for each_book in the_list:
        if isinstance(each_book,list):
            fun_book(each_book)
        else:
            print(each_book)
