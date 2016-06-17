import unittest  
from libaws.ec2 import subnet
import os

class TestSubnetFunctions(unittest.TestCase):  

    def setUp(self):  
        self.test_dir = os.path.abspath(os.path.split(__file__)[0])
                
    def test_create_subnet(self):  

        yaml_config_file = os.path.join(self.test_dir,'subnet_config.yaml')
        subnet.create_default_subnet_from_config(yaml_config_file)
                             
if __name__ == '__main__':  
    unittest.main()
