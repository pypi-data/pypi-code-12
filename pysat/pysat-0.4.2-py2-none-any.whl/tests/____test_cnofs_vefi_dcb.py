import pysat

class testVEFI:
    
    def setup(self):
        self.vefi = pysat.Instrument('cnofs', 'vefi', 'dc_b')
        
    def teardown(self):
        del self.vefi
        
    def test_instantiation(self):
        vefi = pysat.Instrument('cnofs', 'vefi', 'dc_b')
        
    def test_download(self):
        start = pysat.datetime(2009,1,1)
        stop = pysat.datetime(2009,1,2)
        self.vefi.download(start, stop)
        
    def test_load(self):
        start = pysat.datetime(2009,1,1)
        self.vefi.load(date=start)