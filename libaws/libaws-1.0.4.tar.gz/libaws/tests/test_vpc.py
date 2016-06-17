import unittest  
from libaws.ec2 import vpc
import os

class TestVPCFunctions(unittest.TestCase):  

    def setUp(self):  
        self.test_dir = os.path.abspath(os.path.split(__file__)[0])
                
    def test_create_vpc(self):  

        yaml_config_file = os.path.join(self.test_dir,'vpc_config.yaml')
        vpc.create_default_vpc_from_config(yaml_config_file)
                             
if __name__ == '__main__':  
    unittest.main()
