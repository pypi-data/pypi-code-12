def printing(the_list, level):
    for i in the_list:
        if isinstance(i,list):
            printing(i,level+1)
        else:
            for tab in range(level):
                print("\t",end=' ')
            print(i)


movies = ["The Holy Grail", 1975, "Terry Jones & Terry Gilliam", 91,
			["Graham Chapman", 
					["Michael Palin", "John Clease", "Terry Gilliam", "Eric Idle", "Terry Jones"]]]


printing(movies,0)
