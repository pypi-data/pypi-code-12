def main():
    for i in range(1,10):
        if i ==1:
            print('%3d'%(i),end="")
        else:
            print('%7d'%(i),end="")
    print()
    for i in range(1,10):
        print('%-2d'%(i),end="")
        for j in range(1,i+1):
            print('%dx%d=%s'%(j,i,format(i*j,'<3d')),end="")
        print()

main()
            
