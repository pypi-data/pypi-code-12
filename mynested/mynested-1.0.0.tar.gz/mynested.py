# this is a comment
def mynested(mylist,level=3):
        for item in mylist:
                if isinstance(item, list):
                        mynested(item,level+1)
                else:
                        for tab_stop in range(level):
                                print("\t",end ='')
                                
                        print(item)

                        
                        
                                      


                                

                                
