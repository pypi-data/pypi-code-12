



COOKIE_FILE="/Users/conerj/ECS_COOKIEDIR/rootcookie"
#HOSTIP="10.4.0.102"


#2.2 system
#HOSTIP="10.77.33.160"

HOSTIP="10.247.198.77"


def printit(result, silent=False):
    if silent == True:
        return
    if(result):
        if isinstance(result, list):
            print("ITS A LIST")
            for record in result:
                print record
        else:
            print result

