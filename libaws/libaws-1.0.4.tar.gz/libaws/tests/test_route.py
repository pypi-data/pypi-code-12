import unittest  
from libaws.ec2 import route
import os

class TestRouteFunctions(unittest.TestCase):  

    def setUp(self):  
        self.test_dir = os.path.abspath(os.path.split(__file__)[0])
                
    def test_create_route(self):  

        yaml_config_file = os.path.join(self.test_dir,'route_config.yaml')
        route.create_default_routetable_from_config(yaml_config_file)
                             
if __name__ == '__main__':  
    unittest.main()
