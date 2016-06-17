import unittest  
from libaws.ec2 import security 
import os

class TestSecurityFunctions(unittest.TestCase):  

    def setUp(self):  
        self.test_dir = os.path.abspath(os.path.split(__file__)[0])
                
    def test_create_security(self):  

        yaml_config_file = os.path.join(self.test_dir,'security_config.yaml')
        security.create_default_security_group_from_config(yaml_config_file)
                             
if __name__ == '__main__':  
    unittest.main()
