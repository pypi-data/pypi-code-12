def BMeTric(Rating,Votes):
    import math
    meanRating,meanVotes,varRating,varVotes,RVcorr = getMoments()
    
    zRating = (Rating-meanRating)/(varRating**0.5)
    zVotes = (math.log10(Votes)-meanVotes)/(varVotes**0.5)
    
    return 100*NCDF(-zRating,zVotes,RVcorr)

def NCDF(z1,z2,r):
    import math
    
    #http://www.math.wsu.edu/faculty/genz/software/matlab/bvnl.m
    if r==0:
        p = math.erfc( -z1/math.sqrt(2) )/2*math.erfc( -z2/math.sqrt(2) )/2
    else:
        tp = 2*math.pi
        h = z1
        k = z2
        hk = h*k
        bvn = [0]

        w = [.01761400713915212,.04060142980038694,.06267204833410906,
             .08327674157670475,0.1019301198172404,0.1181945319615184,
             0.1316886384491766,0.1420961093183821,0.1491729864726037,
             0.1527533871307259]
        x = [0.9931285991850949,0.9639719272779138,0.9122344282513259,
             0.8391169718222188,0.7463319064601508,0.6360536807265150,
             0.5108670019508271,0.3737060887154196,0.2277858511416451,
             0.07652652113349733]
        w = w+w;
        x = [1-a for a in x] + [1+a for a in x]

        if abs(r)>0.925:
            print("ERROR: correlation too high for this algorithm")
            p = 0
        else:
            hs = (h*h+k*k)/2
            asr = math.asin(r)/2
            sn = [math.sin(asr*a) for a in x]
            bvn = [math.exp((sn[i]*hk*hs)/(1-sn[i]*sn[i]))*w[i] for i in range(len(w))]
            bvn = [a*asr/tp + math.erfc( -h/math.sqrt(2) )/2*math.erfc( -k/math.sqrt(2) )/2 for a in bvn]

        p = max([0]+[min([1]+bvn)])
    return p

def getMoments():
    from numpy import load
    import pkg_resources

    filename = pkg_resources.resource_filename(__name__,'data/IMDBMu.npy')
    
    muB = load(filename)
    Mr = muB[0]
    Mv = muB[1]
    Vr = muB[2]-muB[0]**2
    Vv = muB[4]-muB[1]**2
    r = (muB[3]-muB[0]*muB[1])/(Vr*Vv)**0.5

    return Mr,Mv,Vr,Vv,r

