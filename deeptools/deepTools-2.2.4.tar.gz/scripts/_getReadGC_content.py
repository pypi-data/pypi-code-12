def getReadGCcontent(read, fragmentLength, chrNameBit):
        """
        The fragments for foward and reverse reads are defined as follows

           |- read.pos       |- read.aend
        ---+=================>-----------------------+---------    Forward strand

           |-fragStart                               |-fragEnd

       ----+-----------------------<=================+---------    Reverse strand
                                   |-read.pos        |-read.aend

           |-----------------------------------------|
                            read.tlen
         """    
    global tbit
    if read.is_paired and read.is_proper_pair:
        if read.is_reverse:
            fragEnd   = read.aend
            fragStart = read.aend + read.tlen
        else:
            fragStart = read.pos
            fragEnd   = read.pos + read.tlen
    else:
        if read.is_reverse:
            fragEnd    = read.aend
            fragStart  = read.aend  - fragmentLength
        else:
            fragStart  = read.pos 
            fragEnd    = fragStart + fragmentLength

    # skip if fragment starts or ends beyond the chromosome boundaries
    if fragStart < 0 or fragEnd > tbit[chrNameBit].size:
        return None
    try:
        # calculate GC content of read fragment
        gc = getGC_content(tbit[chrNameBit].get(fragStart, 
                                                fragEnd), 
                               as_fraction=False)
    except Exception as detail:
        print detail 
        """ this exception happens when the end of a chromosome is reached """

    return int(round((float(gc * fragmentLength) / abs(read.tlen)))
