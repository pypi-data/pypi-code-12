import unittest  
from libaws.ec2 import instance 
import os

class TestInstanceFunctions(unittest.TestCase):  

    def setUp(self):  
        self.test_dir = os.path.abspath(os.path.split(__file__)[0])
                
    def test_create_instance(self):  
        yaml_config_file = os.path.join(self.test_dir,'instance_config.yaml')
        self.instance = instance.create_default_instance_from_config(yaml_config_file)
        instance.ssh_connect_instance(self.instance)
    
    def test_connect_instance(self):  
        instance.ssh_connect_instance(self.instance)
                            
if __name__ == '__main__':  
    unittest.main()
