try:
    from src.gimpy import Graph
except:
    from coinor.gimpy import Graph

if __name__ == '__main__':
    G = Graph(type = 'digraph', splines = 'true', layout = 'dot',
              display = 'xdot', rankdir = 'LR', 
              label = 'ISE Requirements and Prerequisite Map\n\nFa = Fall, Sp = Spring, Su = Summer',
              fontsize = '120', labelloc = 't', size = "7.5,10.0!", ratio = 'fill',
              esep = '10', ranksep = '1.8',
              )
    node_format = {
#                   'height':1.0,
#                   'width':2.0,
#                   'fixedsize':'true',
                   'fontsize': '60',
#                   'fontcolor':'red',
                    'shape': 'ellipse',
                    'style': 'bold',
                    'fontname': 'Times-Bold' 
                   }
    
    edge_format = {
                   'penwidth': '5.0',
                   'arrowsize': '3.0'
    }

    G.add_node('CSE 2', **node_format)
    G.add_node('Eng 10', **node_format)
    G.add_node('ISE 112', label = 'ISE 112\nFa', **node_format)
    G.add_edge('Eng 10', 'CSE 2', **edge_format)
    G.add_edge('CSE 2', 'ISE 112', style = 'invisible', arrowhead = 'none')
    G.add_node('ISE 172', label = 'ISE 172\nSp', **node_format)
    G.add_node('ISE 215/216', label = 'ISE 215/216\nFa/Su', **node_format)
    G.add_node('CSE 17', **node_format)
    G.add_edge('CSE 2', 'CSE 17', **edge_format)
    G.add_edge('ISE 112', 'CSE 17', style = 'invisible', arrowhead = 'none')
    G.add_node('Mat 33', **node_format)
    G.add_edge('CSE 17', 'ISE 172', **edge_format)
    G.add_edge('Mat 33', 'ISE 215/216', **edge_format)
    G.add_node('ISE 305', label = 'ISE 305\nSp', **node_format)
    G.add_node('Math 21', **node_format)
    G.add_node('Physics 11/12', **node_format)
    G.add_edge('Math 21', 'Physics 11/12', **edge_format)
    G.add_node('Math 22', **node_format)
    G.add_edge('Math 21', 'Math 22', **edge_format)
    G.add_node('Physics 21/22', **node_format)
    G.add_edge('Physics 11/12', 'Physics 21/22', **edge_format)
    G.add_node('Math 23', **node_format)
    G.add_edge('Math 23', 'Physics 21/22', style = 'dashed', **edge_format)
    G.add_edge('Math 22', 'Math 23', **edge_format)
    G.add_node('ISE 111', label = 'ISE 111\nFa/Sp', **node_format)
    G.add_edge('Math 22', 'ISE 111', **edge_format)
    G.add_node('Math 205', **node_format)
    G.add_edge('Math 22', 'Math 205', **edge_format)
    G.add_node('ISE 121', label = 'ISE 121\nFa/Sp', **node_format)
    G.add_edge('ISE 111', 'ISE 121', **edge_format)
    G.add_node('Mech 2/3', **node_format)
    G.add_node('ME 104', **node_format)
    G.add_node('ECE 83/81', **node_format)
    #G.add_node('Options', label = 'Options*', **node_format)
    G.add_edge('Physics 21/22', 'ECE 83/81', style = 'dashed', **edge_format)
    G.add_edge('Math 22', 'Mech 2/3', stlye = 'dashed', **edge_format)
    G.add_edge('Math 23', 'ME 104', style = 'dashed', **edge_format)
    G.add_edge('Physics 11/12', 'ME 104', style = 'dashed', **edge_format)
    G.add_node('ISE 240', label = 'ISE 240\nFa/Sp', **node_format)
    G.add_edge('Math 205', 'ISE 240', **edge_format)
    G.add_node('ISE 230', label = 'ISE 230\nFa/Su', **node_format)
    G.add_edge('ISE 111', 'ISE 230', **edge_format)
    G.add_node('ISE 131/132', label = 'ISE 131/132\nSp', **node_format)
    G.add_edge('ISE 111', 'ISE 131/132', style = 'dashed', **edge_format)
    G.add_node('ISE 224', label = 'ISE 224\nFa/Sp', **node_format)
    G.add_edge('ISE 121', 'ISE 305', **edge_format)
    G.add_node('ISE 226', label = 'ISE 226\nSp', **node_format)
    G.add_edge('ISE 111', 'ISE 226', **edge_format)
    G.add_node('ISE 251', label = 'ISE 251\nFa', **node_format)
    G.add_edge('ISE 121', 'ISE 251', **edge_format)
    G.add_edge('ISE 240', 'ISE 251', **edge_format)
    G.add_edge('ISE 230', 'ISE 251', **edge_format)
    G.add_node('Engl 1', **node_format)
    G.add_node('Engl 2', **node_format)
    G.add_edge('Engl 1', 'Engl 2', **edge_format)
    G.add_node('Eng 5', **node_format)
    G.add_node('Chem 30', **node_format)
    G.add_node('Eco 1', **node_format)
    G.add_node('Acct 108', label = 'Acct 108\nSp', **node_format)
    G.add_node('ISE 254', label = 'ISE 254\nFa/Sp', **node_format)
    G.add_edge('Engl 2', 'Eng 5', style = 'invisible', arrowhead = 'none')
    G.add_edge('Eng 5', 'Chem 30', style = 'invisible', arrowhead = 'none')
    G.add_edge('Chem 30', 'Eco 1', style = 'invisible', arrowhead = 'none')
    G.add_edge('Eco 1', 'Acct 108', style = 'invisible', arrowhead = 'none')
    G.add_edge('Acct 108', 'ISE 254', style = 'invisible', arrowhead = 'none')
    G.add_node('ISE 339', label = 'ISE 339\nSp', **node_format)
    G.add_edge('ISE 230', 'ISE 339', **edge_format)
    G.add_node('ISE 316', label = 'ISE 316\nFa', **node_format)
    G.add_edge('ISE 240', 'ISE 316', **edge_format)
    G.add_node('ISE 347', label = 'ISE 347\nSp', **node_format)
    G.add_edge('ISE 316', 'ISE 347', **edge_format)
    G.add_node('ISE 275', label = 'ISE 275\nSp', **node_format)
    G.add_edge('ISE 224', 'ISE 275', **edge_format)
    G.add_node('ISE 372', label = 'ISE 372\nFa', **node_format)
    G.add_edge('ISE 275', 'ISE 372', **edge_format)
    G.add_node('ISE 358', label = 'ISE 358\nFa/Su', **node_format)
    G.add_node('ISE 324', label = 'ISE 324\nSp', **node_format)
    G.add_edge('Math 205', 'ISE 324', **edge_format)
    G.add_node('ISE 332', label = 'ISE 332\nSp', **node_format)
    G.add_edge('ISE 121', 'ISE 332', **edge_format)
    G.add_node('ISE 362', label = 'ISE 362\nSp', **node_format)
    G.add_edge('ISE 230', 'ISE 362', **edge_format)
    G.add_edge('ISE 240', 'ISE 362', **edge_format)
    G.add_node('ISE 341', label = 'ISE 341\nFa', **node_format)
    G.add_edge('ISE 230', 'ISE 341', **edge_format)
    G.add_edge('ISE 224', 'ISE 341', **edge_format)
    G.add_edge('ISE 240', 'ISE 341', **edge_format)
    G.add_node('ISE 356', label = 'ISE 356\nFa', **node_format)
    G.add_edge('ISE 230', 'ISE 356', **edge_format)
    G.add_edge('ISE 240', 'ISE 356', **edge_format)
    G.add_node('ISE 355', label = 'ISE 355\nSp', **node_format)
    G.add_edge('ISE 240', 'ISE 355', **edge_format)
    G.add_node('ISE 321', label = 'ISE 321\nFa/Sp/Su', **node_format)
    G.add_node('ISE 382', label = 'ISE 382\nFa/Sp', **node_format)
    G.add_node('ISE 334', label = 'ISE 334\nFa', **node_format)
    G.add_edge('ISE 240', 'ISE 372', **edge_format)
    G.add_edge('ISE 230', 'ISE 372', **edge_format)
    G.add_node('ISE 319', label = 'ISE 319\nFa', **node_format)
    G.add_edge('ISE 131/132', 'ISE 319', **edge_format)
    G.add_node('ISE 340', label = 'ISE 340\nFa', **node_format)
    G.add_edge('ISE 215/216', 'ISE 340', **edge_format)
    G.add_node('CSE 2xx', label = 'CSE 2xx \n except \n 241/252', **node_format)
    G.add_node('CSE 3xx', **node_format)
    G.add_node('BIS 3xx', **node_format)
    G.add_node('Math 230', **node_format)
    G.add_node('ISE 256', label = 'ISE 256\nMust take\nISE 255\nas FE', **node_format)
    G.add_edge('ISE 362', 'CSE 2xx', style = 'invisible', arrowhead = 'none')
    G.add_edge('ISE 362', 'CSE 3xx', style = 'invisible', arrowhead = 'none')
    G.add_edge('ISE 362', 'BIS 3xx', style = 'invisible', arrowhead = 'none')
    G.add_edge('ISE 362', 'Math 230', style = 'invisible', arrowhead = 'none')
    G.add_edge('ISE 362', 'ISE 334', style = 'invisible', arrowhead = 'none')
    G.add_edge('ISE 362', 'ISE 382', style = 'invisible', arrowhead = 'none')
    G.add_edge('ISE 362', 'ISE 256', style = 'invisible', arrowhead = 'none')
    label = \
    '''
    *Engineering Elective Requirements: 
    In addition to the above, courses of 
    3 or more credits from BIOE, CHE, CEE, 
    CSE, ECE, MAT, ME, or MECH may be 
    selected, with exceptions listed at: 
    https://ise.lehigh.edu/content/courses
    '''
    #The list of excluded courses for an individual ISE 
    #student is governed by the catalog in force when
    #the student is admitted to Lehigh. A provisional
    #course offered with one of these prefixes requires 
    #department approval. Any course meeting these 
    #stipulations is denoted "Engineering Elective Requirement"
    #in the ISE program description.
    G.add_node('Eng Req', label = label, fontsize = '72', shape = 'plaintext', fontname = 'Times')
    #G.add_edge('Eng Req', 'Options')
    #cluster_attrs = {'fontsize' : '72', 'name':'Eng Req', 
    #                 'label':'Engineering Elective Requirements'} 
    #G.create_cluster(['Eng Req'], cluster_attrs)

    cluster_attrs = {'fontsize' : '72'} #, 'style' : 'bold'}

    cluster_attrs.update({'name': 'Tracks', 'label': 'Choose One'})    
    G.create_cluster(['ISE 172', 'ISE 215/216'], cluster_attrs)

    cluster_attrs.update({'name':'English', 'label':'English Requirements'})    
    G.create_cluster(['Engl 1', 'Engl 2'], cluster_attrs)

    cluster_attrs.update({'name': 'Eng', 'label':'Engineering Electives\nChoose At Least Four'})
    G.create_cluster(['Mech 2/3', 'ME 104', 'ECE 83/81', 'CSE 17', 'Mat 33', 'Eng Req'], cluster_attrs)

    cluster_attrs.update({'name':'Isolated', 'label':'Miscellaneous Requirements'})
    G.create_cluster(['Eng 5', 'Chem 30', 'Eco 1', 'Acct 108', 'ISE 254'], cluster_attrs)

    cluster_attrs.update({'name':'TE', 
                          'label':'Technical Electives\nChoose at Least 4\n(at Least 2 ISE)'})
    G.create_cluster(['ISE 339', 'ISE 316', 'ISE 347', 'ISE 275', 'ISE 358', 'ISE 324', 
                      'ISE 332', 'ISE 362', 'ISE 341', 'ISE 356', 'ISE 355', 'ISE 321', 
                      'ISE 382', 'ISE 334', 'ISE 372', 'ISE 319', 'ISE 340', 
                      'CSE 2xx', 'BIS 3xx', 'CSE 3xx', 'Math 230',
                      'ISE 256'], 
                     cluster_attrs)

    cluster_attrs.update({'name':'Computing', 'label':'Computing Requirements'})
    G.create_cluster(['CSE 2', 'Eng 10', 'ISE 112'], cluster_attrs)

    G.set_display_mode('file')

    G.display(basename = 'ISERequirements', format = 'pdf')
