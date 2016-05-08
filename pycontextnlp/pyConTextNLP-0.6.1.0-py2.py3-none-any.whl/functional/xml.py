def getXML(mu):
    nodes = mu.nodes(data=True)
    nodes.sort()
    nodeString = u''
    for n in nodes:
        attributeString = u''
        keys = n[1].keys()
        keys.sort()
        for k in keys:
            attributeString += """<{0}> {1} </{2}>\n""".format(k, n[1][k], k)
        modificationString = u''
        modifiedBy = mu.predecessors(n[0])
        if modifiedBy:
            for m in modifiedBy:
                modificationString += u"""<modifiedBy>\n"""
                modificationString += u"""<modifyingNode> {0} </modifyingNode>\n""".format(m.getTagID())
                modificationString += \
                    u"""<modifyingCategory> {0} </modifyingCategory>\n""".format(m.getCategory())
                modificationString += u"""</modifiedBy>\n"""
        modifies = mu.successors(n[0])
        if modifies:
            for m in modifies:
                modificationString += u"""<modifies>\n"""
                modificationString += u"""<modifiedNode> {0} </modifiedNode>\n""".format(m.getTagID())
                modificationString += u"""</modifies>\n"""
        nodeString += tmplts.nodeXMLSkel.format(
            attributeString+"{0}".format(n[0].getXML())+modificationString )
    edges = mu.edges(data=True)
    edges.sort()
    edgeString = u''
    for e in edges:
        keys = e[2].keys()
        keys.sort()
        attributeString = u''
        for k in keys:
            attributeString += """<{0}> {1} </{2}>\n""".format(k, e[2][k], k)
        edgeString += "{0}".format(tmplts.edgeXMLSkel.format(e[0].getTagID(), e[1].getTagID(), attributeString))

    return tmplts.ConTextMarkupXMLSkel.format(tmplts.xmlScrub(get_RawText(mu)),
                                              tmplts.xmlScrub(get_cleanText(mu)),
