"为了对打包模块进行测试"
def outall(k_list,charge=False,times=0):
    for each_item in k_list:
        if isinstance(each_item,list):
            outall(each_item,charge,times+1)
        else:
            if charge:
                for table_k in range(times):
                    print("\t",end='')
            print(each_item)
