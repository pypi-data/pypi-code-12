"""The printing function has three arguments first:list conatining elements, second:True if indentation required
else False, third: the initial level of your list, 0 by default"""
def printing(the_list,indent, level):
    if indent==False:
        level=0
    for i in the_list:
        if isinstance(i,list):
            printing(i,indent,level+1)
        else:
            if indent:
                for tab in range(level):
                    print("\t",end=' ')
            print(i)


movies = ["The Holy Grail", 1975, "Terry Jones & Terry Gilliam", 91,
			["Graham Chapman", 
					["Michael Palin", "John Clease", "Terry Gilliam", "Eric Idle", "Terry Jones"]]]


printing(movies,False,5)
