# this is a comment
def mynested(mylist,indent = False, level=0):
        for item in mylist:
                if isinstance(item, list):
                        mynested(item,indent, level+1)
                else:
                     if indent:   
                        for tab_stop in range(level):
                                print("\t",end ='')
                     print(item)

                     
                                
                 

                        

                        
                        
                                      


                                

                                
