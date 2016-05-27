

class GeneralOutput:
    """
    The GeneralOuptut class should be subclassed by the output plugin.
    
    :param dict sitesData: The data from sites in the form of a dictionary.  The keys should be the sites, and the values should be an array of times for the transfers.
    
    .. _sitesData-label:
    
    An example structure for ``sitesData`` is::
    
        sitesData = {
            "UCSDT2": [
                {'starttime': "140192910", 'endtime': "140204950", 'successful': True}, 
                {'starttime': "140105910", ...}
            ], 
            "Nebraska": [
                {'starttime': ...}]}
                ...
    
    The initialize function should also be used to initialize any structures required for processing.
    """
    
    def __init__(self, sitesData):
        self.sitesData = sitesData
        
    def startProcessing(self):
        """
        This is called when the the output plugin should begin processing the `sitesData` data.
        
        """
        pass
        
