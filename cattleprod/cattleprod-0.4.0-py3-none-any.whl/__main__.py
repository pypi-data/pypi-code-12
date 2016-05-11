import cattleprod

if __name__=="__main__":
    # python 2-3 divergence
    try: input = raw_input
    except NameError: pass
    url = input("Enter rancher base URL: ")
    print("Looking for projects ...")
    c = cattleprod.connect(url)
    print(c)
    i = 1
    for p in c.get_projects():
        print("{}. '{}' (id: {})".format(i, p.name, p.id))
        i+=1
